import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results
from common import SharedChapterClass, SharedSeriesClass
import common
from urllib import parse
import json

urls = ['comix.to']

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/title/[^/]+/[^/]+/?'
    # refer to common.py's SharedChapterClass in this same spot for an explanation of thise code
    image_headers = {}
    add_host_to_image_headers = False
    replace_image_failed_error_with_warning = False
    add_host_but_call_it_something_else = None # this should be a string of what it should be if used
    def __init__(self, url: str):
        super().__init__(url)

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        from scrapers.comix import Chapter

        chapter = Chapter('https://comix.to/title/pvry-one-piece/7217327-chapter-1169')
        img_urls = chapter.get_img_urls()
        print(img_urls)'''
        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now we turn that into a string, which we then parse
        # the images are in a script tag, so we find that first then parse it
        # we go about this by parsing the html, getting all the script tag's scripts, and filtering those until we're left with what we want
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # getting all the script tags' text
        script_tags_text: list[str] = [script_tag.text for script_tag in soup.find_all('script')]

        # now we filter them by filtering out all the ones that don't have a link that leads to an image (i.e. example.com/.../a.jpg or example.com/.../b.webp)
        script_tags_with_links_text: list[str] = []
        for script_tag_text in script_tags_text:
            # this is just we go through every image file extension we recongize, (defined in common.py (image_file_extensions_with_periods/image_file_extensions_without_periods)) and check if the script tag has it
            for file_extension in common.image_file_extensions_with_periods:
                if script_tag_text.lower().__contains__(file_extension):
                    script_tags_with_links_text.append(script_tag_text)
                    break

        # now we get the zero-th element of the list, since that should be the only one, and have our urls
        # if there's multiple, we raise an error
        if len(script_tags_with_links_text) != 1:
            raise Exception(f'Error when getting image urls for {self.url}. Expected to only get one valid script tag with images, instead found multiple. Please open a bug report. (Expected 1, got {len(script_tags_with_links_text)})')
        
        # now we parse it
        img_urls = [
            url_hashmap_stuff.split('\\')[1].lstrip('"') # this line uses the next line to get the actual url
            for url_hashmap_stuff in script_tags_with_links_text[0].split('\\"prev\\"')[0].split('\\"url\\":')[1:] # this line gets the (I believe) hashmap with the images
            ]

        # then we return it
        return img_urls


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/title/[^/]+/?'
    chapter_object_reference = Chapter
    def __init__(self, url: str):
        super().__init__(url)

    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        from scrapers.comix import Series

        series = Series('https://comix.to/title/pvry-one-piece')
        chapter_urls = series.get_chapter_urls()
        print(chapter_urls)'''
        # what we do here is somewhat different from the other scrapers
        # instead of requesting the page, we use their api endpoint
        # it just needs an id, which is the first part of the url (the pvry part of https://comix.to/title/pvry-one-piece)
        # so, we first request page 1 (since it's we can only request the urls for 100 chapters at once)
        # then that'll tell us how many more pages to request
        series_id = self.url.split('title/')[1].split('-')[0]

        # we use a wierd for loop, since I don't wanna have to write the logic for getting the url twice
        # so instead we just start with 1 page total, and then update that every time
        # so from the response, we see there's 14 pages to request total, cool
        # then for the next request, we still change the variable

        # we also make a variable to store the chapter AND DATA
        # the data part is used in the next bit
        chapter_data: list[dict] = []

        page_count = 1
        i = 0
        while i < page_count:
            # increasing i
            i += 1

            # requesting the url
            response = requests.get(f'https://{urls[0]}/api/v2/manga/{series_id}/chapters?limit=100&page={i}&order[number]=asc')

            # making sure we got a status code 200
            if response.status_code != 200:
                raise Exception(
                    f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')
                        
            # parsing the response's json
            # we can just get result, since the only other thing is status, which should be 200
            response_json: dict = json.loads(response.content.decode()).get('result')
            
            # adding the chapter data to our list of chapter data
            chapter_data = chapter_data + response_json.get('items')

            # updating the page count
            page_count = int(response_json.get('pagination').get('last_page'))

        # now the reason we haven't just extracted the urls is a few reasons
        # A, there's multiple different scans/sources for one chapter (like mangadex)
        # B, we can also prioritize getting the official translation over unofficial scanlations/scans
        # we can sort for official entries, because there's a variable for the chapter, and a variable for if it's official
        # even more specifically, we go through the list, and we keep a list of the chapters we've scanned
        # if we hit a chapter that we haven't gotten a url for, then we get every chapter for the chapter number, and prioritize using the official url
        # if there is no url, we just use index 0
        # this is (I believe) O(n^2), but it should be fine since it's a pretty small number, and python is pretty fast
        scanned_chapter_numbers = []
        urls = []
        for specific_chapter_data in chapter_data:
            # getting the chapter number
            chapter_number = specific_chapter_data.get('number')

            # checking if we haven't already looked at this chapter
            if not scanned_chapter_numbers.__contains__(chapter_number):
                # adding it to the list of scanned chapter numbers
                scanned_chapter_numbers.append(chapter_number)

                # getting every chapter's data for this chapter number, and taking the best one from those
                chapters_with_that_chapter_number = []
                for chapter in chapter_data:
                    if type(chapter) == dict and chapter.get('number') == chapter_number:
                        chapters_with_that_chapter_number.append(chapter)

                # going through and adding a chapter to the urls if it's offical
                # we also have a variable to store if we found an official one for this chapter
                found_official = False
                for this_specific_chapter_data in chapters_with_that_chapter_number:
                    if this_specific_chapter_data.get('is_official') == 1:
                        # adding the url
                        urls.append(f'{self.url.rstrip('/')}/{this_specific_chapter_data.get('chapter_id')}')

                        # setting that we found an official one to true
                        found_official = True

                        # breaking out of the loop
                        break
                
                if not found_official:
                    # otherwise, if ther was no official one, we just add index 0
                    urls.append(f'{self.url.rstrip('/')}/{specific_chapter_data.get('chapter_id')}')

        return urls
    

    def get_name(self) -> str:
        # this basically gets the part after title/, then removes the bit before the first -
        # that's because it goes [id]-name-of-thing, so we're just removing the id
        return '-'.join(self.url.split('title/')[1].split('-')[1:])


# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses comix.to's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://www.{urls[0]}/api/v2/manga?keyword={url_safe_query}&order[relevance]=desc'

    # these are the headers
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(f'Recieved status code {query_response.status_code} when searching \'{query}\' on {urls[0]}')

    # now we parse the json
    response_json: dict = json.loads(query_response.content.decode()).get('result')

    # then we go through everything in the items part of the json and add a it as a SearchResult to the list of search results
    search_results = []
    for search_result_json in response_json.get('items'):
        # adding it to the list of search results
        search_results.append(SearchResult(search_result_json.get('title'), # title
                                           f'https://{urls[0]}/title/{search_result_json.get('hash_id')}-{search_result_json.get('slug')}', # url
                                           'comix') # website id
                                           )

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results
import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results
from common import SharedChapterClass, SharedSeriesClass
from urllib import parse

urls = ['1manga.co']

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/chapter/[^/]*/chapter-\d*(\.\d)?/?'
    # refer to common.py's SharedChapterClass in this same spot for an explanation of thise code
    image_headers = {}
    add_host_to_image_headers = False
    replace_image_failed_error_with_warning = False
    add_host_but_call_it_something_else = None # this should be a string of what it should be if used
    def __init__(self, url: str):
        super().__init__(url)


    def get_img_urls(self) -> list[str]:
        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # first we get the div inside the div with all our images in it
        # this div has the id 'adblock-wrapper', so that's why it's called what it is
        adblock_wrapper_div = soup.find('div', {'id': 'adblock-wrapper'})

        # next we get that div's parent, which will also be the div with all the images in it
        image_div = adblock_wrapper_div.parent

        # then we get the src of the first img
        # we do this because the layout of where every image is is wierd, so we just manipulate the url since it's <first_bit_of_url>/1.<filename>, <first_bit_of_url>/2.<filename>, etc
        first_img_src = image_div.find('img').get('src')

        image_headers = {
            'Referer': 'https://1manga.co/'
        }

        # after that we go by 10s and go until a url doesn't exist
        i = 10
        while True:
            # the first step is constructing the url
            # so we extract the filetype and filename
            filetype = first_img_src.split('.')[-1]

            # then we also get the rest of the url
            filename = '.'.join(first_img_src.split('.')[:-1])

            # now we change the filename to be for the image we're looking to find
            # (aka we just change the last character to i
            # we also add the filetype so we have our full url
            full_url = f'{filename[:-1]}{str(i)}.{filetype}'

            # now we request the url, if it exists, we continue, if it doesn't we break out of the loop
            if requests.head(full_url, headers=image_headers).status_code != 404:
                i += 10
            else:
                break

        # now we just try going down from i, and seeing if that image exists, until one exists
        # once we find that image that exists, we know that's our image count
        for subtracting_from_i in range(11):
            # constructing the url
            filetype = first_img_src.split('.')[-1]
            filename = '.'.join(first_img_src.split('.')[:-1])
            full_url = f'{filename[:-1]}{str(i - subtracting_from_i)}.{filetype}'

            # now we request the url
            if requests.head(full_url, headers=image_headers).status_code != 404:
                # since it existed, we save the image count and break out of the loop
                image_count = i - subtracting_from_i
                break
            # otherwise we just let the loop continue

        # finally we just construct all the image urls we need
        image_urls = []
        for i in range(1, image_count + 1):
            # constructing the url
            filetype = first_img_src.split('.')[-1]
            filename = '.'.join(first_img_src.split('.')[:-1])
            full_url = f'{filename[:-1]}{str(i)}.{filetype}'

            # now we add the url we constructed to image_urls
            image_urls.append(full_url)


        return image_urls

    def get_name(self) -> str:
        return self.url.strip('/').split('/')[-1]


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/manga/[^/]*/?'
    chapter_object_reference = Chapter
    def get_chapter_urls(self) -> list[str]:
        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # next since there can be multiple tabs of chapters (1-100, 101-200, etc), we get the thing that contains all this
        div_with_the_chapter_pages = soup.find('div', {'class': 'tab-content'})

        # after that, we get one chapter from the div_with_the_chapter_pages
        # we do this because the site has some anti scraper measures meaning there's fake <a> tags with wrong links. So, we get an example one, and all the correct links have the same class, so once we figure out the class, we just get everything with that class
        chapter_example = div_with_the_chapter_pages.find('div').find('ul').find('li')

        # then we get this chapter's number (i.e. #225.5, or #127, etc)
        chapter_number_text = chapter_example.find('span', {'class': 'text-secondary'}, recursive=True).text

        # next we extract an actual number from the text we got, since that text still has the chapter's name
        # this is still a string, but we won't need to convert it for our purposes
        chapter_number = chapter_number_text.split(' ')[0].replace('#', '')

        # now that we have that, we get all the <a> tags, and figure out which one has the correct link
        a_tags = chapter_example.find_all('a', recursive=True)

        for a_tag in a_tags:
            # first we get the final bit of the url's path
            final_part_of_the_url_path = parse.urlparse(a_tag.get('href')).path.strip('/').split('/')[-1]

            # then we check remove the 'chapter-' bit from it, and check if it equals our chapter number
            if final_part_of_the_url_path.replace('chapter-', '') == chapter_number:
                # since it was correct we save the class as the correct class
                correct_a_tag_class = a_tag.get('class')[0]

        # now we get every <a> tag with that class, and extract it's url
        chapter_urls = []
        for a_tag in soup.find_all('a', {'class': [correct_a_tag_class]}, recursive=True):
            chapter_urls.append(a_tag.get('href'))

        # then we reverse the order of the chapter urls so the first chapter is at index 0
        chapter_urls.reverse()

        # finally we return the chapter urls we just got
        return chapter_urls
    

# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses 1manga.co's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://www.1manga.co/search?q={url_safe_query}&page=1&order=POPULAR'

    # we add a thing to make it show adult content if enabled
    if adult:
        search_url += '&genre=adult'

    # these are the headers
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code == 404:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on mangabuddy.com')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # getting the div with all the results in it
    results_div = soup.find('div', {'class': 'row'})

    # checking if there were any search results
    if results_div.text.strip() == 'No Manga found!':
        return []

    # then we go through every div with the media-manga class and extract that search results data and add it to the list of search results
    search_results = []
    for search_result_div in results_div.find_all('div', {'class': 'media-manga'}):
        # first we get the div with everything we the <h4> tag that has the <a> tag with everything we need
        h4_tag = search_result_div.find('h4', recursive=True)

        # then we get the a tag we want in that h4 tag
        a_tag_we_want = h4_tag.find('a')

        # finally we make a SearchResult object with data from that <a> tag
        search_results.append(
            SearchResult(a_tag_we_want.text.strip(), a_tag_we_want.get('href'), '1manga')
        )

    # then we sort the search results and return them!
    sorted_search_results = sort_search_results(search_results, query)
    return sorted_search_results
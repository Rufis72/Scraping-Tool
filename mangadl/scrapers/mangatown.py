import bs4
import requests
from bs4 import BeautifulSoup
from mangadl.common import SearchResult, sort_search_results
from mangadl.common import SharedChapterClass, SharedSeriesClass
from urllib import parse

urls = ['mangatown.com']

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/manga/[^/]*/(v\d*/)?c\d\d\d+(/\d+\.html)?/?'
    # refer to common.py's SharedChapterClass in this same spot for an explanation of thise code
    image_headers = {'Referer': 'https://www.mangatown.com/'}
    add_host_to_image_headers = True
    replace_image_failed_error_with_warning = False
    add_host_but_call_it_something_else = 'Alt-Used' # this should be a string of what it should be if used
    def __init__(self, url: str):
        super().__init__(url)

    def get_img_urls(self) -> list[str]:
        # giving an update that we're getting image urls, since it can take a while
        print(f'Getting the image urls for {self.url}')

        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # mangatown has one image per page, so we have to request all those pages
        # the first step in doing that is getting the image count
        # there's a dropdown menu that has buttons for every image on the chapter, so we have to get that
        image_dropdown = soup.find('select', {'onchange': 'javascript:location.href=this.value;'})

        # then we get the text from the dropdown
        image_dropdown_text = image_dropdown.text.strip()

        # now we go through every item in the image dropdown text seperated by spaces and try converting it to a number
        # if that works, then we save that as the image_count, and continue with the loop
        # if it fails (because it reached the 'Featured' part at the end of the list) it'll break out of the loop, and that last saved image_count is our image count!
        for dropdown_item_text in image_dropdown_text.split(' '):
            try:
                image_count = int(dropdown_item_text.lstrip('0'))
            except:
                break

        # here we give an update for every image downloaded
        print(f'{self.url}: Image page 0/{image_count}', end='')

        img_urls = []

        # now that we have the image count, we get every page and get it's image
        for image_number in range(1, image_count + 1):
            url = f'{self.url.strip('/')}/{image_number}.html'

            # requesting the url
            response = requests.get(url)

            # making sure we got a status code 200
            if response.status_code != 200:
                raise Exception(
                    f'Recieved status code {response.status_code} when requesting the page at \'{url}\'')

            # now that we know the request went through, we parse the webpage
            soup = bs4.BeautifulSoup(response.content, 'html.parser')

            # then we get the img and add it to the list of imgs
            img_urls.append('https://' + soup.find('img', {'id': 'image'}).get('src').strip('/'))

            # we also give an update that we finished getting that image page
            print(f'\r{self.url}: Image page {image_number}/{image_count}', end='')

        # now we print something to finish off the image page updates
        print(f'\r{self.url}: Image page {image_count}/{image_count}')

        # finally we return the imgs we got
        return img_urls

    def get_name(self) -> str:
        return self.url.strip('/').split('/')[-1]



class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/manga/[^/]*/?'
    chapter_object_reference = Chapter
    def __init__(self, url):
        super().__init__(url)


    def get_chapter_urls(self) -> list[str]:
        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # first we make sure that the content wasn't dmca-ed
        if soup.find('div', {'class': 'chapter_content'}).text.__contains__('it is not available in MangaTown'):
            print(f'{self.url} is not avalible on mangatown, it seems to have been dmca-ed. \"{soup.find('div', {'class': 'chapter_content'}).text.strip()}\"')
            return []

        # now we get the <ul> with all the chapter urls in it
        chapter_ul = soup.find('ul', {'class': 'chapter_list'})

        # then we go through and get all the <li> in the chapter_ul's <a> tag's href and add it to the list of urls
        chapter_urls = []
        for chapter_li in chapter_ul.find_all('li'):
            chapter_urls.append('https://mangatown.com' + chapter_li.find('a').get('href'))

        # before we return everything, since at the top is the latest chapter currently, and we want index 0 to be the first, not the last
        chapter_urls.reverse()

        # finally we just return all the urls
        return chapter_urls


def search(query: str, adult: bool or None = None) -> list[SearchResult]:
    '''Uses mangatown.com's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://www.mangatown.com/search?name={url_safe_query}&page=1'

    # these are the headers
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on mangatown.com')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # then we get the <ul> with all the search result data
    ul_with_search_results = soup.find('ul', {'class': 'manga_pic_list'})

    # here we check if ul_with_search_results is None, since that would mean there weren't any search results
    if not ul_with_search_results:
        return []

    # after that we go through every title <p> tag with the class 'title' and extract the name and href
    search_results = []
    for p_tag_in_search_results in ul_with_search_results.find_all('p', {'class': 'title'}, recursive=True):
        # then we get the <a> tag in the <p> tag we just got
        # this a tag will have the actual name and link
        a_tag = p_tag_in_search_results.find('a')

        # finally we just make a search result object and add it to the list
        search_results.append(SearchResult(a_tag.get('title'), 'https://mangatown.com' + a_tag.get('href'), 'mangatown'))

    # finally we just sort the search results with our own sorting function
    sorted_search_results = sort_search_results(search_results, query)

    # then we just return the list of search results we made!
    return sorted_search_results
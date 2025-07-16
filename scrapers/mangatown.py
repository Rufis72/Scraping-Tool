import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results
from common import SharedChapterClass, SharedSeriesClass
from urllib import parse

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www.)?mangatown\.com/manga/[^/]*/c\d\d\d+/\d+\.html/?'
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

        # next we get the div with all the images
        image_div = soup.find('div', {'id': 'viewer'})

        # then we go through every <a> tag and get the img inside of it's src
        img_urls = []
        for a_tag in image_div.find_all('a'):
            img_urls.append('https:' + a_tag.find('img').get('src'))

        # now we return the urls
        return img_urls

    def download(self, output_path: str, show_updates_in_terminal: bool = True, replace_image_failed_error_with_warning: bool = False):
        super().download(output_path, show_updates_in_terminal, {'Referer': 'https://www.mangatown.com/'}, True, replace_image_failed_error_with_warning)


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?mangatown\.com/manga/[^/]*/?'
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
    
    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        super().download(output_path, Chapter, show_updates_in_terminal)


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
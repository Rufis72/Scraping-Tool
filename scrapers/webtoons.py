import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results # this is stuff for search results
from common import SharedChapterClass, SharedSeriesClass # this is the base shared classes for Chapter and Series
import re
from urllib import parse

class Chapter(SharedChapterClass):
    def __init__(self, url: str):
        super().__init__(url)

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        # initializing the chapter object
        chapter = Chapter('https://www.webtoons.com/en/action/hero-killer/episode-1/viewer?title_no=2745&episode_no=1')

        # getting the urls
        img_urls = chapter.get_img_urls()

        # printing the urls
        print(img_urls)'''
        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # next we get the div with all the images in it
        img_div = soup.find('div', {'id': '_imageList'})

        # next we go through every image in the img_div and save it to our list of images
        image_srcs = []
        for image in img_div.find_all('img'):
            # now we get the img's src and add it to our list of images
            image_srcs.append(image.get('data-url'))

        # finally we return the image sources
        return image_srcs

    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        super().download(output_path, show_updates_in_terminal, image_headers={'Referer': 'https://www.webtoons.com/'}, add_host_to_image_headers=True)

    def get_name(self) -> str:
        # first we parse the url
        parsed_url = parse.urlparse(self.url)

        # then we get the path of the url
        url_path = parsed_url.path.strip('/')

        # now we split the url by slashes, and get the second to last one (which is the chapter name)
        chapter_name = url_path.split('/')[-2]

        # finally we return the chapter name
        return chapter_name

class Series(SharedSeriesClass):
    def __init__(self, url: str):
        super().__init__(url)

    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        # initializing the series object
        series = Series('https://www.webtoons.com/en/action/hero-killer/list?title_no=2745')

        # getting the urls to the chapters
        chapter_urls = series.get_chapter_urls()

        # printing the chapter's urls
        print(chapter_urls)'''

        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # after that, we get the div with all the chapters
        chapter_div = soup.find('ul', {'id': '_listUl'})

        # webtoons.com requires a slightly different approach since it doesn't put all a series's chapters on 1 page
        # but that's easy to get around, since you can just add &episode_no=<episode number here> to go to a specific episode
        # so what we do is just get the first episode, then count down until we hit episode 1
        latest_chapter_div = chapter_div.find('li')

        # next we get the <a> tag in the chapter row div
        a_tag_with_href = latest_chapter_div.find('a')

        # then we get the a tag's href and save it as the latest chapter url
        latest_chapter_url = a_tag_with_href.get('href')

        # extracting the amount of chapters from the url
        chapter_amount = int(latest_chapter_url.split('episode_no=')[1])

        # finally we just make the urls for every chapter, since we can just add &episode_no=<episode number here> and it'll redirect to the correct chapter
        chapter_urls = []
        for i in range(chapter_amount):
            chapter_urls.append(f'{latest_chapter_url.split('episode_no=')[0]}episode_no={i+1}'
                                .replace(f'episode-{chapter_amount}', f'episode-{i+1}')) # this second line here is just to improve readability while debugging

        # now we just return the chapter urls
        return chapter_urls


    def download(self, output_path: str):
        super().download(output_path, Chapter)

    def get_name(self) -> str:
        # first we get the url's path
        url_path = parse.urlparse(self.url).path

        # then we remove and slashes at the beginning or end
        url_path = url_path.strip('/')

        # finally we split the url_path by slashes and get the second to last item
        series_name = url_path.split('/')[-2]

        # now that we have the name, we just return it!
        return series_name


# all the functions here are for main.py
def identify_url_type(url: str) -> None or 'chapter' or 'series':
    '''Returns the type of a url. 'type' meaning if it's a series, chapter, or if it isn't a valid url for this scraper

    Example Code:

    from scrapers.webtoons import identify_url_type

    print(identify_url_type('https://www.webtoons.com/en/action/hero-killer/list?title_no=2745'))
    :param url: The url to identify the type of
    :return: Either 'chapter', 'series', or None'''
    # these are the regular expressions we'll be checking against
    chapter_regex = re.compile(r'(https://)?(www\.)?webtoons\.com/[^/]+/[^/]+/[^/]+/[^/]+/viewer\?title_no=\d+&episode_no=\d+/?')
    series_regex = re.compile(r'(https://)?(www\.)?webtoons\.com/[^/]+/[^/]+/[^/]+/list/?\?title_no=\d+(&page=\d+)?')

    # now we check them
    if chapter_regex.fullmatch(url):
        return 'chapter'
    elif series_regex.fullmatch(url):
        return 'series'
    else:
        print('b')
        return None


def search(query: str, adult: bool or None = None):
    '''Uses webtoons.com's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://www.webtoons.com/en/search/originals?keyword={url_safe_query}&page=1'

    # these are the headers for requesting the search query
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on webtoons.com')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # first we check if we got any results
    if soup.find('div', {'class': 'no_data'}) != None:
        return []

    # next we get the div with all the results in it
    chapter_div = soup.find('ul', {'class': 'webtoon_list'})

    # next we go through everything in that div and extract the name and url and save it as a SearchResult object to our list of search results
    search_results = []
    for search_result in chapter_div.find_all('li'):
        url = search_result.find('a').get('href')
        name = search_result.find('strong', {'class': 'title'}).text.strip()

        # now we turn it into a search result object and save it
        search_results.append(SearchResult(name, url, 'webtoons'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results
import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results
from common import SharedChapterClass, SharedSeriesClass
from urllib import parse

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?natomanga\.com/manga/[^/]*/chapter-[^/]+/?'
    def __init__(self, url: str):
        super().__init__(url)

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        from scrapers.natomanga import Chapter

        chapter = Chapter('https://www.natomanga.com/manga/the-beginning-after-the-end/chapter-224/')
        img_urls = chapter.get_img_urls()
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
        img_div = soup.find('div', {'class': 'container-chapter-reader'})

        # next we go through every image in the img_div and save it to our list of images
        image_srcs = []
        for image in img_div.find_all('img'):
            # now we get the img's src and add it to our list of images
            image_srcs.append(image.get('src'))

        # finally we return the image sources
        return image_srcs


    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        super().download(output_path, show_updates_in_terminal, image_headers={'Referer': 'https://www.natomanga.com/'}, add_host_to_image_headers=True, replace_image_failed_error_with_warning=True)



class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?natomanga\.com/manga/[^/]*/?'
    def __init__(self, url: str):
        super().__init__(url)

    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        from scrapers.natomanga import Series

        series = Series('https://www.natomanga.com/manga/the-beginning-after-the-end/')
        chapter_urls = series.get_chapter_urls()
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
        chapter_div = soup.find('div', {'class': 'chapter-list'})

        # then we get all the links from everything in chapter_div
        chapter_urls = []
        for chapter_row in chapter_div.find_all('div'):
            # first we get the <a> tag in the chapter row div
            a_tag_with_href = chapter_row.find('a')

            # then we get the a tag's href and add it to the list
            chapter_urls.append(a_tag_with_href.get('href'))

        # the second to last step is to reverse the list, because otherwise index 0 would be the latest chapter
        chapter_urls.reverse()

        # the final step is just returning the urls
        return chapter_urls
    
    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        super().download(output_path, Chapter, show_updates_in_terminal=show_updates_in_terminal)


# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses natomanga.com's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://www.natomanga.com/search/story/{url_safe_query}?page=1'

    # these are the headers
    headers = {
        'Host': 'www.natomanga.com',
        'Referer': 'https://www.natomanga.com/',
    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(f'Recieved status code {query_response.status_code} when searching \'{query}\' on natomanga.com')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # next we get the div with all the result in it
    chapter_div = soup.find('div', {'class': 'panel_story_list'})

    # next we go through everything in that div and extract the name and url and save it as a SearchResult object to our list of search results
    search_results = []
    for search_result in chapter_div.find_all('div'):
        url = search_result.find('a').get('href')
        name = search_result.find('h3', {'class': 'story_name'}).text.strip()
        # now we turn it into a search result object and save it
        # because for whatever reason, there's always two of something in the search results, we check if we've already added that thing
        # if it's already there, we just don't add it
        if len(search_results) == 0 or search_results[-1].url != url:
            search_results.append(SearchResult(name, url, 'manganato'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results
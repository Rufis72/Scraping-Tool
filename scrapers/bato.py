import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results
from common import SharedChapterClass, SharedSeriesClass
from urllib import parse

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?bato\.to/chapter/(\d+)/?'
    def __init__(self, url: str):
        super().__init__(url)
        

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        from scrapers.bato import Chapter

        chapter = Chapter('https://bato.to/chapter/1809486')
        img_urls = chapter.get_img_urls()
        print(img_urls)'''
        # first we request the series page
        response = requests.get(self.url)

        # making sure we got a status code 200
        if response.status_code != 200:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # next, since bato puts it's img urls in a javascript array, we find that array, and get all the images
        img_array_text = response.text.split('const imgHttps = [')[1].split(']')[0]

        # then we turn it into an array
        image_urls = [text.strip('"') for text in img_array_text.split(', ')]

        # finally we return the images as a list
        return image_urls


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?bato\.to/series/\d+/[^/]+/?'
    def __init__(self, url: str):
        super().__init__(url)


    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        from scrapers.bato import Series

        series = Series('https://bato.to/series/95977/frieren-beyond-journey-s-end-official')
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

        # then we get the div with all the chapter divs in it
        div_with_chapter_divs = soup.find('div', attrs={'class': 'main'})

        # then we go through every div in it and get the chapter url
        chapter_urls = []
        skipped_div_count = 0
        for chapter_div in div_with_chapter_divs.find_all('div'):
            # if it doesn't have the div for the visited chapter, we just skip it
            # this is expected behavior, and it seems to have the right side of the chapters ui on the website
            # there is one for every actual chapter <a>, so we count how many there are, and if the two aren't equal, we warn the user
            if chapter_div.find('a', attrs={'class': 'visited chapt'}) == None:
                skipped_div_count += 1
            else:
                chapter_urls.append('https://bato.to' + chapter_div.find('a', attrs={'class': 'visited chapt'}).get('href'))

        # warning the user if more than one was skipped
        if skipped_div_count != len(chapter_urls):
            print(f'When downloading the seires at {self.url}, there were {skipped_div_count} skipped divs, instead of the expected {len(chapter_urls)} (the amount of chapter urls there are). Please create an issue on the Github repo at https://github.com/Rufis72/Scraping-Tool/issues')

        # after that we reverse it so the last chapter isn't at index 0
        chapter_urls.reverse()

        # the final step is just returning the urls
        return chapter_urls


    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        super().download(output_path, Chapter, show_updates_in_terminal=show_updates_in_terminal)


# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses bato.to's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://bato.to/search?word={url_safe_query}'

    # these are the headers
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on bato.to')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # getting the div with all the results in it
    results_div = soup.find('div', {'id': 'series-list'})

    # checking if there were any search results
    if soup.find('div', {'class': 'browse-no-matches'}) != None:
        return []

    # next we go through everything in that div and extract the name and url and save it as a SearchResult object to our list of search results
    search_results = []
    for search_result in results_div.find_all('div', {'class': 'col'}):
        # we add the domain since the links are shortened like this: /name-of-thing
        url = 'https://bato.to' + search_result.find('div', attrs={'class': 'item-text'}).find('a', attrs={'class': 'item-title'}).get('href')
        name = search_result.find('div', attrs={'class': 'item-text'}).find('a', attrs={'class': 'item-title'}).text

        # now we turn it into a search result object and save it
        search_results.append(SearchResult(name, url, 'bato'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results

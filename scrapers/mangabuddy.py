import os.path
import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results # these are search related items
from common import SharedChapterClass, SharedSeriesClass # these are series and chapter related items
from common import construct_chapter_not_found_image # these are error message related items
import re
from urllib import parse

class Chapter(SharedChapterClass):
    def __init__(self, url: str):
        super().__init__(url)

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        from scrapers.mangabuddy import Chapter

        chapter = Chapter('https://mangabuddy.com/the-beginning-after-the-end/chapter-224')
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

        # next we get the script tag that has all the images in a variable in it
        chapter_images_script = soup.find('div', {'id': 'viewer-page'}).find_all('script', recursive=False)[1]

        # now we extract the string-ified list of all the image urls
        stringified_url_list = chapter_images_script.string.strip().split('\'')[1]

        # finally we return the images as a list
        return stringified_url_list.split(',')

    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        super().download(output_path, show_updates_in_terminal, image_headers={'Referer': 'https://mangabuddy.com/'})


class Series(SharedSeriesClass):
    def __init__(self, url: str):
        super().__init__(url)


    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        from scrapers.mangabuddy import Series

        series = Series('https://mangabuddy.com/the-beginning-after-the-end')
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

        # now we get the script with the bookID
        script_with_book_id = soup.find('body').find('script')

        # now we extract the bookID from the javascript of the script_with_book_id
        bookID = script_with_book_id.string.strip().split('\n')[0].split('= ')[1].replace(';', '')

        # now that we have the book ID, we can request the full chapter list (but it'll be html, so we'll have to parse it)
        html_full_chapter_list_response = requests.get(f'https://mangabuddy.com/api/manga/{bookID}/chapters?source=detail')

        # then we make sure that request went through
        if html_full_chapter_list_response.status_code != 200:
            raise Exception(f'Recieved status code {html_full_chapter_list_response.status_code} when requesting the expanded list of chapters at: \'https://mangabuddy.com/api/manga/{bookID}/chapters?source=detail\'')

        # now we parse that response
        full_chapter_list_soup = BeautifulSoup(html_full_chapter_list_response.content, 'html.parser')

        # finally we can just go through every <a> and get it's href
        chapter_urls = []
        for a_tag in full_chapter_list_soup.find_all('a'):
            chapter_urls.append('https://mangabuddy.com' + a_tag.get('href'))

        # before we return the urls, we have to flip them since in the html, the latest chapter is at the top, and we go from top to bottom
        chapter_urls.reverse()

        # the final step is just returning the urls
        return chapter_urls


    def download(self, output_path: str):
        super().download(output_path, Chapter)


# all the functions here are for main.py
def identify_url_type(url: str) -> None or 'chapter' or 'series':
    '''Returns the type of a url. 'type' meaning if it's a series, chapter, or if it isn't a valid url for this scraper

    Example Code:

    from scrapers.mangabuddy import identify_url_type

    print(identify_url_type('https://mangabuddy.com/the-beginning-after-the-end/'))
    :param url: The url to identify the type of
    :return: Either 'chapter', 'series', or None'''
    # these are the regular expressions we'll be checking against
    chapter_regex = re.compile(r'(https://)?(www\.)?mangabuddy\.com/[^/]*/chapter-[^/]+/?')
    series_regex = re.compile(r'(https://)?(www\.)?mangabuddy\.com/[^/]*/?')

    # now we check them
    if chapter_regex.fullmatch(url):
        return 'chapter'
    elif series_regex.fullmatch(url):
        return 'series'
    else:
        return None


def search(query: str, adult: bool or None = None):
    '''Uses mangabuddy.com's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://www.mangabuddy.com/search?q={url_safe_query}&page=1'

    # we add a thing to make it show adult content if enabled
    if adult:
        search_url += '&genre[]=adult'

    # these are the headers
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on mangabuddy.com')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # getting the div with all the results in it
    chapter_div = soup.find('div', {'class': 'list manga-list'})

    # checking if there were any search results
    if soup.find('div', {'class': 'search-empty'}) != None:
        return []

    # next we go through everything in that div and extract the name and url and save it as a SearchResult object to our list of search results
    search_results = []
    for search_result in chapter_div.find_all('div', {'class': 'title'}):
        # we add the domain since the links are shortened like this: /name-of-thing
        url = 'https://mangabuddy.com' + search_result.find('a').get('href')
        name = search_result.find('a').get('title')

        # now we turn it into a search result object and save it
        search_results.append(SearchResult(name, url, 'mangabuddy'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results

def download_chapter(series_url: str, chapter_num: int, output_path: str):
    '''Donwloads the chapter_numth chapter of a series. If the chapter number does not exist, or is invalid, it will give the user dialog to pick another option

    Example Code:

    from scrapers.mangabuddy import download_chapter

    download_chapter('https://mangabuddy.com/the-beginning-after-the-end', 224)
    :param series_url: The url of the series
    :param chapter_num: The index of the chapter to be downloaded
    :param output_path: Where the chapter's images will be saved'''
    # first we make a series object for the series
    series_object = Series(series_url)

    # next we get all the chapter urls for that series
    chapter_urls = series_object.get_chapter_urls()

    # after that we check if the chapter_num is a valid index for the chapter_urls (aka it's not 99999 and there's only 7 chapters)
    try:
        # this does two things. First it checks if the chapter_num is valid, then it gets the url to the chapter we're downloading
        chapter_to_download_url = chapter_urls[chapter_num]

    except:
        # checking if there's no chapters just in case
        if len(chapter_urls) == 0:
            print(f'Sorry! \'{series_url}\' doesn\'t seem to have any chapters!')

        # now we get the input from the user for what chapter num they want to download
        new_user_chapter_num = int(input(construct_chapter_not_found_image(chapter_urls, chapter_num)))

        # then the last step before downloading is getting the url corresponding to that number
        chapter_to_download_url = chapter_urls[new_user_chapter_num]


    # now we download the chapter
    # even if the chapter_num wasn't valid, it'll still save the new chapter_url to chapter_to_download_url
    download(chapter_to_download_url, output_path)
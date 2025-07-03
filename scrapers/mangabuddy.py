import os.path
import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results # these are search related items
from common import SharedChapterClass, SharedSeriesClass # these are series and chapter related items
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
def download(url: str, output_path: str):
    '''Checks if the url works for this scraper, and if so downloads and saves the contents from the url, then returns True. Otherwise, it does nothing and returns False

    Example Code:
    from scrapers.mangabuddy import download

    download('https://mangabuddy.com/the-beginning-after-the-end') # this will return True and download it
    :param url: The url we are checking if matches, and if so downloading
    :param output_path: The output path to save the downloaded images to'''
    # these are the regex for the chapter and series respectively
    chapter_regex = re.compile(r'(https://)?(www\.)?mangabuddy\.com/[^/]*/chapter-[^/]+/?')
    series_regex = re.compile(r'(https://)?(www\.)?mangabuddy\.com/[^/]*/?')

    # here we check if either match the given url
    if chapter_regex.fullmatch(url) or series_regex.fullmatch(url):
        # if the code got here, we know it matches so next we check if it's a series or chapter, then download it accordingly
        # this is for series
        if series_regex.fullmatch(url):
            # since it matched, we give an indication it matched to the user
            print(f'Downloading {url}')

            # first we make an object for the series
            series_object = Series(url)

            # after that we make the directory for the series. (if we're not already in it)
            # if we are already in the directory for the series directory, the following code will be False and nothing will happen
            if os.path.basename(output_path) != url.strip('/').split('/')[-1]:
                # if the directory for the series directory doesn't exist, we make it
                if not os.path.exists(os.path.join(output_path, url.strip('/').split('/')[-1])):
                    os.mkdir(os.path.join(output_path, url.strip('/').split('/')[-1]))
                # now we justt change the output path to the new directory for the series one so we can just pass output_path to the download function either way
                output_path = os.path.join(output_path, url.strip('/').split('/')[-1])


            # next we download the images
            # the download function also saves them, so we don't have to worry aobut that
            series_object.download(output_path)

            # then we return True so whatever is calling this knows it matched
            return True

        # this is for chapters
        elif chapter_regex.fullmatch(url):
            # since it matched, we give an indication it matched to the user
            print(f'Downloading {url}')

            # first we make an obejct for the chapter
            chapter_object = Chapter(url)

            # next we download the images
            chapter_object.download(output_path)

            # then we return True so whatever is calling this knows it matched
            return True

    else:
        # here we return false since it didn't match anything
        return False


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
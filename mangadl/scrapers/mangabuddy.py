import bs4
import requests
from bs4 import BeautifulSoup
from mangadl.common import SearchResult, sort_search_results
from mangadl.common import SharedChapterClass, SharedSeriesClass
from urllib import parse

urls = ['mangabuddy.com']

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/[^/]*/chapter-[^/]+/?'
    # refer to common.py's SharedChapterClass in this same spot for an explanation of thise code
    image_headers = {'Referer': 'https://mangabuddy.com/'}
    add_host_to_image_headers = False
    replace_image_failed_error_with_warning = False
    add_host_but_call_it_something_else = None # this should be a string of what it should be if used
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

        # making sure we got an ok response
        if not response.ok:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # next we get all the script tags in the website to then sort through to find the correct script tag
        chapter_images_scripts = soup.find('div', {'id': 'viewer-page'}).find_all('script', recursive=False)
        # now we go through and get the correct script tag
        for scrip_tag in chapter_images_scripts:
            if scrip_tag.string.__contains__('chapImages'):
                stringified_url_list = scrip_tag.string.strip().replace('var chapImages = ', '').replace('\'', '')

        # finally we return the images as a list
        return stringified_url_list.split(',')


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/[^/]*/?'
    chapter_object_reference = Chapter
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

        # making sure we got an ok response
        if not response.ok:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the series at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # now we get the script with the book_id
        script_with_book_id = soup.find('body').find('script')

        # now we extract the book_id from the javascript of the script_with_book_id
        book_id = script_with_book_id.string.strip().split('\n')[0].split('= ')[1].replace(';', '')

        # now that we have the book ID, we can request the full chapter list (but it'll be html, so we'll have to parse it)
        html_full_chapter_list_response = requests.get(f'https://mangabuddy.com/api/manga/{book_id}/chapters?source=detail')

        # then we make sure that request went through
        if html_full_chapter_list_response.status_code != 200:
            raise Exception(f'Recieved status code {html_full_chapter_list_response.status_code} when requesting the expanded list of chapters at: \'https://mangabuddy.com/api/manga/{book_id}/chapters?source=detail\'')

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


# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses mangabuddy.com's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://mangabuddy.com/search?q={url_safe_query}&page=1'

    # we add a thing to make it show adult content if enabled
    if adult:
        search_url += '&genre[]=adult'

    # these are the headers
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got an ok response
    if not query_response.ok:
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
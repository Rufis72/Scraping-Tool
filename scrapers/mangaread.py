import bs4
import requests
from common import SearchResult, sort_search_results
from common import SharedChapterClass, SharedSeriesClass
import urllib.parse

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?mangaread\.org/manga/[^/]*/chapter-[^/]+/?'
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
        from scrapers.mangaread import chapter

        chapter = Chapter('https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-224/')
        img_urls = chapter.get_img_urls()
        print(img_urls)'''
        # first we request the chapter
        response = requests.get(self.url)

        # next we make sure we make sure we got a status code 200
        if response.status_code != 200:
            raise Exception(f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # now that we know the request went through, we parse the webpage
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # the first step to getting the images is navigating the url and getting the reading content div
        # the reading content div has all the images
        reading_content_div = soup.find('div', {'class': 'reading-content'})

        # now the final step is to get all images and extract their srcs
        img_srcs = []
        # here we go through every image and get it's src
        for img in reading_content_div.find_all('img'):
            # now we add the img's src to img_srcs
            img_srcs.append(img.get('src').strip())

        # now the final final step is to return all the urls we got
        return img_srcs


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?mangaread\.org/manga/[^/]*/?'
    chapter_object_reference = Chapter
    def __init__(self, url: str):
        super().__init__(url)

    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of the urls to all the chapters of a series as strings

        Example Code:
        from scrapers.mangaread import Series

        s = Series('https://www.mangaread.org/manga/the-beginning-after-the-end/')
        urls = s.get_chapter_urls()
        print(urls)'''
        # first we request the page url
        response = requests.get(self.url)

        # next we make sure we got a status code 200
        if response.status_code != 200:
            raise Exception(f'Error when requesting the series at \'{self.url}\'. Got status code {response.status_code}')

        # now that we know the request went through, we parse the html
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        # finally we go through every element in that list and get the link it leads to
        chapter_urls = []
        # the reason we call it chapter_li is because the chapter buttons are li tags
        for chapter_li in  soup.find_all('li', {'class': 'wp-manga-chapter'}):
            # we get the a tag for the chapter because that's what has the href
            chapter_a_tag = chapter_li.find('a')
            # now we append the a tag's href to the chapter urls, and on to the next chapter_li!
            chapter_urls.append(chapter_a_tag.get('href'))

        # but before returning the urls, we have to flip the list so the last chapter isn't at index 0, and the first isn't at -1
        chapter_urls.reverse()

        # now the final final thing is returning the urls we just extracted
        return chapter_urls

# all the functions here are for main.py
def search(query: str, adult:  bool or None = None) -> list[SearchResult]:
    '''Uses mangaread.org's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a query we can later put into a url
    url_safe_query = urllib.parse.quote(query)

    # next we get the url we'll be requesting
    query_url = f'https://mangaread.org/?s={url_safe_query}&post_type=wp-manga'

    # adding the filter for adult content if specified
    if adult == True:
        # if adult is true, it shows only adult content
        query_url += '&adult=1'
    elif adult == False:
        # if adult is false, it shows only not adult content
        query_url += '&adult=0'
    else:
        # otherwise if not specified it shows both
        query_url+='&adult='

    # after that we actually request the url
    query_response = requests.get(query_url)

    # here we make sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(f'Recieved status code {query_response.status_code} when searching \'{query}\' on mangaread.org')

    # now that we know the search went through, we parse the html we just got
    soup = bs4.BeautifulSoup(query_response.content, 'html.parser')

    # first we check if we got any search results at all, if we didn't, we []
    if soup.find('div', {'class': 'not-found-content'}) != None:
        return []

    # secondly we get the div that has all the search results
    search_result_div = soup.find('div', {'class': 'c-tabs-item', })

    # this is the div where we save all the search results
    search_results = []

    # now we go through every row in the div and get it's name, and url
    for search_result in search_result_div.find_all('div', {'class': 'c-tabs-item__content'}):
        # first we get the title
        title = search_result.find('div', {'class': 'post-title'}).text.strip()

        # then we get the url
        url = search_result.find('a').get('href')

        # now we add the data we just got as a SearchResult object to the list of search_results
        search_results.append(SearchResult(title, url, 'mangaread'))

    # then the second to last step is feeding the search results through our own searching function
    # that function basically just sorts them all by how similar their names are to the query

    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the search results
    return sorted_search_results
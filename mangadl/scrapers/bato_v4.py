import bs4
import requests
from bs4 import BeautifulSoup
from mangadl.common import SearchResult, sort_search_results
from mangadl.common import SharedChapterClass, SharedSeriesClass
from urllib import parse

# these are grabbed from https://batomirrors.pages.dev/
# the other mirrors from the above domain are into bato.py, this file is just for the v4 sites
urls = ['bato.si', 'bato.ing']


class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/title/(\d+)/[^/]+/?'
    # refer to common.py's SharedChapterClass in this same spot for an explanation of thise code
    image_headers = {}
    add_host_to_image_headers = False
    replace_image_failed_error_with_warning = False
    add_host_but_call_it_something_else = None # this should be a string of what it should be if used

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        from scrapers.bato_v4 import Chapter

        chapter = Chapter('https://bato.si/title/103147-shikanoko-nokonoko-koshitantan-official')
        img_urls = chapter.get_img_urls()
        print(img_urls)'''
        print(self.url)
        # first we request the series page
        headers = {
            "Cookie": 'tfv=1766448708679; wd=1860x448',
        }

        response = requests.get(self.url, headers=headers)

        # making sure we got an ok response
        if not response.ok:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # next we parse the html
        soup = BeautifulSoup(response.content, 'html.parser')

        # then we get all the divs with images in them
        image_divs = soup.find_all('div', {'data-name': 'image-item'})

        # now we go and get all the urls
        image_urls = []
        for img_div in image_divs:
            # now we get the div in the div
            div_in_the_image_specific_div = img_div.find('div')

            # then we get the img and add it's src
            image_urls.append(div_in_the_image_specific_div.find('img').get('src'))

        # finally we return the images as a list
        return image_urls


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/title/[^/]+/?'
    chapter_object_reference = Chapter
    def __init__(self, url: str):
        super().__init__(url)


    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        from scrapers.bato_v4 import Series

        series = Series('https://bato.si/title/74597-spy-x-family-official')
        chapter_urls = series.get_chapter_urls()
        print(chapter_urls)'''
        # first we make a variable for the post request json
        request_data = {
            'query': '''query get_comic_chapterList($comicId: ID!, $start: Int) {
                get_comic_chapterList(comicId: $comicId, start: $start) {
                    id
                    data {
                        urlPath
                    }
                }
                }''',
            'variables': {
                'comicId': self.url.split('title/')[1].split('/')[0].split('-')[0],
                'start': -1,
            },
        }

        # then the url for the api
        api_url = f'https://{urls[0]}/ap2/'

        # then the headers
        headers = {

        }

        # first we request the series page
        response = requests.post(api_url, json=request_data, headers=headers)

        # making sure we got an ok response
        if not response.ok:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the api at \'{api_url}\'')

        # now we get the response json, and specifically the part we want
        response_json = response.json().get('data').get('get_comic_chapterList')

        # now we get the chapter urls from the json
        chapter_urls = []
        for chapter_json in response_json:
            chapter_urls.append(f'https://{urls[0]}{chapter_json.get('data').get('urlPath')}')

        # the final step is just returning the urls
        return chapter_urls


# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses bato.si's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # here we use the (not publicly exposed) api at /ap2
    # so first we make the request data
    request_data = {
        'query': '''query get_search_comic($select: Search_Comic_Select) {    
            get_search_comic(select: $select) {      
                items {        
                    data {          
                        urlPath
                        name    
                    }      
                }    
            }  
        }''',
        'variables': {
            'select': {
                'page': 1,
                'size': 10000,
                'sortby': None,
                'word': query
            }
        }
    }

    # constructing the api url
    api_url = f'https://{urls[0]}/ap2/'

    # headers
    headers = {

    }

    # then after that we request the api
    query_response = requests.post(api_url, json=request_data, headers=headers)

    # making sure we got an ok response
    if not query_response.ok:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on {urls[0]}')
    
    # now we get the array of search results from the response json
    response_query_search_result_array = query_response.json().get('data').get('get_search_comic').get('items')

    # next we go through everything in that div and extract the name and url and save it as a SearchResult object to our list of search results
    search_results = []
    for search_result in response_query_search_result_array:
        # we add the domain since the links are shortened like this: /name-of-thing
        url = f'https://{urls[0]}{search_result.get('data').get('urlPath')}'
        name = search_result.get('data').get('name')

        # now we turn it into a search result object and save it
        search_results.append(SearchResult(name, url, 'batov4'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results
import bs4
import requests
from bs4 import BeautifulSoup
from mangadl.common import SearchResult, sort_search_results
from mangadl.common import SharedChapterClass, SharedSeriesClass
from urllib import parse

urls = ['mangadex.org']

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/chapter/[^/]+/?'
    # refer to common.py's SharedChapterClass in this same spot for an explanation of thise code
    image_headers = {'User-Agent': 'https://github.com/Rufis72/mangadl'}
    add_host_to_image_headers = False
    replace_image_failed_error_with_warning = False
    add_host_but_call_it_something_else = None # this should be a string of what it should be if used
    def __init__(self, url: str):
        super().__init__(url)

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        from scrapers.mangadex import Chapter

        chapter = Chapter('https://mangadex.org/chapter/a1d761a5-cfdf-4a50-a203-9be3cb4b930f')
        img_urls = chapter.get_img_urls()
        print(img_urls)'''
        # first we construct get the data we're gonna use to request the api
        chapter_id = self.url.split('chapter/')[1].split('/')[0]

        # constructing the url
        api_url_request = f'https://api.{urls[0]}/at-home/server/{chapter_id}'

        # sending a request to the api
        headers = {
            'User-Agent': 'https://github.com/Rufis72/mangadl'
        }
        response = requests.get(api_url_request, headers=headers)

        # making sure we got an ok response
        if not response.ok:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')
        
        # then we get the json
        response_json: dict = response.json()

        # now we go through and construct all the urls
        img_urls = []
        for filename in response_json.get('chapter').get('data'):
            img_urls.append(f'{response_json.get('baseUrl')}/data/{response_json.get('chapter').get('hash')}/{filename}')

        # finally we return the image sources
        return img_urls


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/title/[^/]+(/[^/]+)?/?'
    chapter_object_reference = Chapter
    def __init__(self, url: str):
        super().__init__(url)

    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        from scrapers.mangadex import Series

        series = Series('https://mangadex.org/title/a1c7c817-4e59-43b7-9365-09675a149a6f/one-piece')
        chapter_urls = series.get_chapter_urls()
        print(chapter_urls)'''
        # first we construct get the data we're gonna use to request the api
        manga_id = self.url.split('title/')[1].split('/')[0]

        # constructing the url
        api_url_request = f'https://api.{urls[0]}/manga/{manga_id}/feed'

        # sending a request to the api
        headers = {
            'User-Agent': 'https://github.com/Rufis72/mangadl'
        }
        response = requests.get(api_url_request, headers=headers, params={'translatedLanguage[]': ['en']})

        # now we get the json from the reseponse
        response_json: dict = response.json()

        # then we format all the urls
        # we have a variable to store if we skipped availible chapters because they were on a seperate site
        skipped_chapters = False
        chapter_urls = []
        for chapter_data in response_json.get('data'):
            if chapter_data.get('attributes').get('externalUrl') is None:
                chapter_urls.append(f'https://{urls[0]}/chapter/{chapter_data.get('id')}')
            else:
                skipped_chapters = True

        # telling the user that we skipped chapter(s) if we did
        if skipped_chapters:
            print('Some chapters were skipped when grabbing chapter urls because the chapter(s) were on a seperate (unsupoorted) site')

        # the final step is just returning the urls
        return chapter_urls


# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses mangadex.org's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we request mangadex's api
    response = requests.get(f'https://api.{urls[0]}/manga', params={'title': query})

    # then we get the response's json
    response_json: dict = response.json().get('data')

    # now we turn the response into a list of SearchResult objects
    search_results = []
    for search_result_data in response_json:
        url = f'https://{urls[0]}/title/{search_result_data.get('id')}'
        name = (search_result_data.get('attributes').get('title')
        .get(next(iter(search_result_data.get('attributes').get('title')))) # the purpose of this line is to get whatever is in title. it could be {'en': '[TITLE]'} or {'ja-ro': '[TITLE]'}, or a gajillion other things, so we just get the first thing in the dict
        )
        
        # now we turn that data into a SearchResult object
        search_results.append(SearchResult(name, url, 'mangadex'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results
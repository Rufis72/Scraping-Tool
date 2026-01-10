import bs4
import requests
from bs4 import BeautifulSoup
from mangadl.common import SearchResult, sort_search_results
from mangadl.common import SharedChapterClass, SharedSeriesClass
from urllib import parse
import json

urls = ['tapas.io']

class Chapter(SharedChapterClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/episode/[\d]+/?'
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
        from scrapers.tapas import Chapter

        chapter = Chapter('https://tapas.io/episode/1123711')
        img_urls = chapter.get_img_urls()
        print(img_urls)'''
        # first we request the series page
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'
        }
        response = requests.get(self.url, headers=headers)

        # making sure we got an ok response
        if not response.ok:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the chapter at \'{self.url}\'')

        # parsing the response
        soup = BeautifulSoup(response.content, features='html.parser')

        # next we get the <article> with the images in it
        image_container = soup.find('article', {'class': ['viewer__body', 'js-episode-article', 'main__body']})

        # if the image container has nothing, the chapter's either paywalled, or requires a sign in
        if image_container is None:
            print(f'Chapter at {self.url} is either paywalled, or requires an account to view. Skipping...')
            return []

        # then we get all the image's sources
        image_urls = []
        for image in image_container.find_all('img'):
            image_urls.append(image.get('data-src'))

        # finally we return the images as a list
        return image_urls


class Series(SharedSeriesClass):
    regex = r'(https://)?(www\.)?' + f'({'|'.join([url.replace('.', r'\.') for url in urls])})' + r'/series/[^/]+/?'
    chapter_object_reference = Chapter
    def __init__(self, url: str):
        super().__init__(url)


    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        from scrapers.tapas import Series

        series = Series('https://tapas.io/series/tbate-comic/')
        chapter_urls = series.get_chapter_urls()
        print(chapter_urls)'''
        # first we ge the series id and first episode's id
        # we use that for the enxt section
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'
        }
        response = requests.get(self.url, headers=headers)

        # making sure we got an ok response
        if not response.ok:
            raise Exception(
                f'Recieved status code {response.status_code} when requesting the series episode endpoint at \'{url}\'')

        # getting the data
        first_episode_id = (
            response.content.decode('utf-8').split('<link rel="canonical" href="')[1].split('"')[0] # this first line get's the url
            .rstrip('/').split('/')[-1] # then this second line turns the url into some numbers. (so .../episode/numbers/ -> numbers)
        )
        series_id = (
            response.content.decode('utf-8').split('<meta property="al:ios:url" content="tapastic://series/')[1].split('"')[0]
        )

        # then we make the template for the chapter url we'll be requesting
        # the way tapas does it is they have a url you can request that will give you (at most) 20 episodes at a time, so we need to make multiple requests
        # the url will look something like this: https://tapas.io/series/111423/episodes?eid=1123711&sort=OLDEST&max_limit=20&page=[PAGE HERE]
        # the page part at the end is the group of episode we're requesting
        # so page 1 is epsiodes 1-20, page 2 is 21-40, etc
        # the reason we don't just change the amount of episodes we get at a time (max_limit) is it limits it to 20
        episode_request_url_template = f'https://tapas.io/series/{series_id}/episodes?eid={first_episode_id}&sort=OLDEST&max_limit=20&page='

        # requesting episode urls until the amount we get back is less than 0
        # the logic for this is if there are 47 episodes, then first we'll get 20, then 20, then 7. So we know once we get 7, it's the last one we'll get with data
        # and if it's a multiple of 20, then the last one will just be 0
        response_episode_count = 20
        page = 0
        episode_urls = []
        while response_episode_count == 20:
            # incrementing the count of the page we're requesting
            page += 1

            # constructing the url
            url = episode_request_url_template + str(page)

            # requesting the url
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Referer': self.url
            }
            response = requests.get(url, headers=headers)

            # making sure we got an ok response
            if not response.ok:
                raise Exception(
                    f'Recieved status code {response.status_code} when requesting the series episode endpoint at \'{url}\'')

            # parsing the response
            response_dict = json.loads(response.content.decode('utf-8'))

            # getting the episodes' urls and adding them to the list
            for episode_data in response_dict.get('data').get('episodes'):
                # all we get is the id, so we have to construct the url
                # for reference, the id is the episode id
                # we format it so it's https://tapas.io/episode/[ID here]
                episode_urls.append('https://tapas.io/episode/' + str(episode_data.get('id')))

            # setting the response episode count
            response_episode_count = len(response_dict.get('data').get('episodes'))

        # returning the urls
        return episode_urls


# all the functions here are for main.py
def search(query: str, adult: bool or None = None):
    '''Uses tapas.io's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://tapas.io/search?q={url_safe_query}'

    # these are the headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'
    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got an ok response
    if not query_response.ok:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on tapas')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # getting the <ul> with all the results in it
    results_div = soup.find('ul', {'class': 'content-list-wrap'})

    # next we go through everything in that div and extract the name and url and save it as a SearchResult object to our list of search results
    search_results = []
    for search_result in results_div.find_all('li', {'class': 'search-item-wrap'}):
        # we add the domain since the links are shortened like this: /name-of-thing
        url = 'https://tapas.io' + search_result.find('a').get('href')
        name = search_result.find('p').text.strip()

        # now we turn it into a search result object and save it
        search_results.append(SearchResult(name, url, 'tapas'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results

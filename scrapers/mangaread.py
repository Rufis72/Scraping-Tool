import os.path
import bs4
import pyperclip
import requests
from common import SearchResult, sort_search_results # these are search related items
from common import SharedChapterClass, SharedSeriesClass # these are series and chapter related itemsimport re
import urllib.parse
import re

class Chapter(SharedChapterClass):
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


    def download(self, output_path: str):
        super().download(output_path, Chapter)

# all the functions here are for main.py
def download(url: str, output_path: str):
    '''Checks if the url works for this scraper, and if so downloads and saves the contents from the url, then returns True. Otherwise, it does nothing and returns False

    Example Code:
    from scrapers.mangaread import download

    download('https://www.mangaread.org/manga/the-beginning-after-the-end/') # this will return True and download it
    :param url: The url we are checking if matches, and if so downloading
    :param output_path: The output path to save the downloaded images to'''
    # these are the regexs for the chapter and series respectively
    chapter_regex = re.compile(r'(https://)?(www\.)?mangaread\.org/manga/[^/]*/chapter-[^/]+/?')
    series_regex = re.compile(r'(https://)?(www\.)?mangaread\.org/manga/[^/]*/?')

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
    pyperclip.copy(query_response.content.decode())

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

def download_chapter(series_url: str, chapter_num: int, output_path: str):
    '''Donwloads the chapter_numth chapter of a series. If the chapter number does not exist, or is invalid, it will give the user dialog to pick another option

    Example Code:

    from scrapers.mangaread import download_chapter

    download_chapter('https://www.mangaread.org/manga/the-beginning-after-the-end/', 224)
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
        # here we construct the dialog we're gonna give to the user
        # we want the dialog to look something like this:

        # '<put chapter_num here>' was not a valid chapter. These are the options to download. Type the number before the ':' to download that chapter
        # 0: <url no. 1>
        # 1: <url no. 2>
        # etc

        # we also check if there's no chapters just in case
        if len(chapter_urls) == 0:
            print(f'Sorry! \'{series_url}\' doesn\'t seem to have any chapters!')

        # this is constructing the '0: <url no. 1>' string
        url_list_dialog = ''
        for i, chapter_url in enumerate(chapter_urls):
            url_list_dialog += f'{i}: {chapter_url}\n'

        # constructing the full dialog
        full_dialog = f'{chapter_num} wasn\'t a valid chapter. There are only {len(chapter_urls)} chapters. These are the available chapters to download. To download one, type the number before the \':\'.\n{url_list_dialog}'

        # now we get the input from the user for what chapter num they want to download
        new_user_chapter_num = int(input(full_dialog))

        # then the last step before downloading is getting the url corresponding to that number
        chapter_to_download_url = chapter_urls[new_user_chapter_num]


    # now we download the chapter
    # even if the chapter_num wasn't valid, it'll still save the new chapter_url to chapter_to_download_url
    download(chapter_to_download_url, output_path)
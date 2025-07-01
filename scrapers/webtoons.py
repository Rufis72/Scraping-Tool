import os.path
import bs4
import requests
from bs4 import BeautifulSoup
from common import SearchResult, sort_search_results, print_image_download_start, print_image_download_update, print_image_download_end
import re
from urllib import parse

class Chapter:
    def __init__(self, url: str):
        self.url = url

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:
        # initializing the chapter object
        chapter = Chapter('https://www.webtoons.com/en/action/hero-killer/episode-1/viewer?title_no=2745&episode_no=1')

        # getting the urls
        img_urls = chapter.get_img_urls()

        # printing the urls
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
        img_div = soup.find('div', {'id': '_imageList'})

        # next we go through every image in the img_div and save it to our list of images
        image_srcs = []
        for image in img_div.find_all('img'):
            # now we get the img's src and add it to our list of images
            image_srcs.append(image.get('data-url'))

        # finally we return the image sources
        return image_srcs

    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        '''Gets all the image urls for a chapter, then downloads them.
        This function will also save the images

        Example Code:
        from natomanga import Chapter

        path_to_save_images_to = 'put/your/path/here'

        # making the chapter object
        chapter = Chapter('https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-224/')

        # downloading the images
        img_bytes = chapter.download(path_to_save_images_to)
        :param output_path: The path the images will be saved to
        :param show_updates_in_terminal: If updates should be shown in terminal when downloading
        '''
        # first we get all the img urls
        img_urls = self.get_img_urls()

        # next we make a directory for the chapter (if it doesn't already exist)
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        # if enabled we print an update in terminal showing we've started the download
        if show_updates_in_terminal:
            print_image_download_start(self.url, len(img_urls))

        # we also define the headers for downloading images here
        image_headers = {
            'Referer': 'https://www.webtoons.com/',
            'Host': parse.urlparse(img_urls[0]).hostname, # we get the hostname of the images since it  changes every chapter
        }

        for i, img_url in enumerate(img_urls):
            # first we request the img
            img_response = requests.get(img_url)

            # next we make sure the request went through
            if img_response.status_code != 200:
                # we also store the status code in case we need to use it for an error message
                status_code_one = img_response.status_code
                # if it didn't, we request it one more time
                img_response = requests.get(img_url, headers=image_headers)

                # and if that still doesn't work, we raise an error
                if img_response.status_code != 200:
                    raise Exception(
                        f'Got status codes {status_code_one} and {img_response.status_code} when requesting the image at \'{img_url}\'')

            # if we did get the image, we save it
            with open(os.path.join(output_path, f'{i:03d}.png'), 'wb') as f:
                f.write(img_response.content)

            # we also give an update that we finished an image (if enabled)
            if show_updates_in_terminal:
                print_image_download_update(self.url, i, len(img_urls))

        # here we print the same text we already printed to show that the chapter's downloaded, but with \n at the end to stop the output becoming all wonky after downloading a chapter
        # if enabled of course
        if show_updates_in_terminal:
            print_image_download_end(self.url, len(img_urls))

class Series:
    def __init__(self, url: str):
        self.url = url

    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of all the chapter urls for a given series

        Example Code:
        # initializing the series object
        series = Series('https://www.webtoons.com/en/action/hero-killer/list?title_no=2745')

        # getting the urls to the chapters
        chapter_urls = series.get_chapter_urls()

        # printing the chapter's urls
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
        chapter_div = soup.find('ul', {'id': '_listUl'})

        # webtoons.com requires a slightly different approach since it doesn't put all a series's chapters on 1 page
        # but that's easy to get around, since you can just add &episode_no=<episode number here> to go to a specific episode
        # so what we do is just get the first episode, then count down until we hit episode 1
        latest_chapter_div = chapter_div.find('li')

        # next we get the <a> tag in the chapter row div
        a_tag_with_href = latest_chapter_div.find('a')

        # then we get the a tag's href and save it as the latest chapter url
        latest_chapter_url = a_tag_with_href.get('href')

        # extracting the amount of chapters from the url
        chapter_amount = int(latest_chapter_url.split('episode_no=')[1])

        # finally we just make the urls for every chapter, since we can just add &episode_no=<episode number here> and it'll redirect to the correct chapter
        chapter_urls = []
        for i in range(chapter_amount):
            chapter_urls.append(f'{latest_chapter_url.split('episode_no=')[0]}episode_no={i+1}'
                                .replace(f'episode-{chapter_amount}', f'episode-{i+1}')) # this second line here is just to improve readability while debugging

        # now we just return the chapter urls
        return chapter_urls

    def download(self, output_path: str):
        '''Gets every chapter of a series' images and saves them to output_path
        If output_path's basename is the name of the series, it will put all the chapters there, otherwise, it will create a folder to save the chapters to

        Example Code:
        from natomanga import Series

        path_to_save_images_to = 'put/your/path/here'

        # making the series object
        series = Series('https://www.natomanga.com/manga/the-beginning-after-the-end')

        # downloading the images
        img_bytes = series.download(output_path)
        :param output_path: The path where the images will be saved to'''
        # first we get all the urls for the chapters in the series
        chapter_urls = self.get_chapter_urls()

        # next we go through and download every chapter
        for i, chapter_url in enumerate(chapter_urls):
            # the first step is making a chapter object for the chapter
            chapter_object = Chapter(chapter_url)

            # then we download it and add it to downloaded_chapters
            # we also pass the output path
            chapter_object.download(os.path.join(output_path, f'{i:04d}'))

# all the functions here are for main.py
def download(url: str, output_path: str):
    '''Checks if the url works for this scraper, and if so downloads and saves the contents from the url, then returns True. Otherwise, it does nothing and returns False

    Example Code:
    from scrapers.webtoons import download

    download('https://www.webtoons.com/en/action/hero-killer/list?title_no=2745') # this will return True and download it
    :param url: The url we are checking if matches, and if so downloading
    :param output_path: The output path to save the downloaded images to'''
    # these are the regex for the chapter and series respectively
    chapter_regex = re.compile(r'(https://)?(www\.)?webtoons\.com/[^/]+/[^/]+/[^/]+/[^/]+/viewer\?title_no=\d+&episode_no=\d+/?')
    series_regex = re.compile(r'(https://)?(www\.)?webtoons\.com/[^/]+/[^/]+/[^/]+/list/?\?title_no=\d+(&page=\d+)?')

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
            # first we get the series name
            series_name = url.strip('/').split('/')[-2]
            # if we are already in the directory for the series directory, the following code will be False and nothing will happen
            if os.path.basename(output_path) != series_name:
                # if the directory for the series directory doesn't exist, we make it
                if not os.path.exists(os.path.join(output_path, series_name)):
                    os.mkdir(os.path.join(output_path, series_name))
                # now we just change the output path to the new directory for the series one so we can just pass output_path to the download function either way
                output_path = os.path.join(output_path, series_name)


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
    '''Uses webtoons.com's search function and returns the top results as a list of SearchResult objects sorted with common.sort_search_results
    :param query: The string to search
    :param adult: If it should include only adult (True), only non-adult (False), or both (None).'''
    # first we turn the query into a url safe query we can later put into a url
    url_safe_query = parse.quote(query)

    # next we put the url safe query into a url
    search_url = f'https://www.webtoons.com/search/originals?q={url_safe_query}&page=1'

    # these are the headers for requesting the search query
    headers = {

    }

    # then after that we request the search page
    query_response = requests.get(search_url, headers=headers)

    # making sure we got a status code 200
    if query_response.status_code != 200:
        raise Exception(
            f'Recieved status code {query_response.status_code} when searching \'{query}\' on webtoons.com')

    # now we parse the html
    soup = BeautifulSoup(query_response.content, 'html.parser')

    # next we get the div with all the results in it
    chapter_div = soup.find('ul', {'class': 'webtoon_list'})

    # next we go through everything in that div and extract the name and url and save it as a SearchResult object to our list of search results
    search_results = []
    for search_result in chapter_div.find_all('li'):
        url = search_result.find('a').get('href')
        name = search_result.find('strong', {'class': 'title'}).text.strip()

        # now we turn it into a search result object and save it
        search_results.append(SearchResult(name, url, 'webtoons'))

    # the second to last step is sorting the search results
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the sorted search results
    return sorted_search_results
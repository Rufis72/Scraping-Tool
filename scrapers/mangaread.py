import bs4
import requests
from common import ImageDownloads, SeriesImageDownloads, Image, SearchResult
import re
import urllib.parse

class Chapter:
    def __init__(self, url: str):
        self.url = url

    def get_img_urls(self) -> list[str]:
        '''Returns a list of all the image urls for a given chapter

        Example Code:

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

    def download(self, show_updates_in_terminal: bool = True) -> ImageDownloads:
        '''Gets all the image urls for a chapter, then downloads them.
        This function returns the bytes of all those images as an ImageDownloads object
        This function will also not save the images, instead if you want to do that call save on the ImageDownloads object this function returns as shown in the example code

        Example Code:
        import os

        path_to_save_images_to = 'put/your/path/here'

        # making the chapter object
        c = Chapter('https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-224\')

        # downloading the images
        img_bytes = c.download()

        # saving the images
        img_bytes.save(path_to_save_images_to)
        '''
        # first we get all the img urls
        img_urls = self.get_img_urls()

        # next, we download all the images and add them to a list
        img_bytes = []

        # if enabled we print an update in terminal showing we've started the download
        if show_updates_in_terminal:
            print(f'{self.url}: Image 0/{len(img_urls)}', end='')

        for i, img_url in enumerate(img_urls):
            # first we request the img
            img_response = requests.get(img_url)

            # next we make sure the request went through
            if img_response.status_code != 200:
                # we also store the status code in case we need to use it for an error message
                status_code_one = img_response.status_code
                # if it didn't, we request it one more time
                img_response = requests.get(img_url)

                # and if that still doesn't work, we raise an error
                if img_response.status_code != 200:
                    raise Exception(f'Got status codes {status_code_one} and {img_response.status_code} when requesting the image at \'{img_url}\'')

            # if we did get the image, we add it to the list
            # we turn the bytearray into a common.Image because common.ImageDownloads uses common.Images as input
            img_bytes.append(Image(img_response.content))

            # we also give an update that we finished an update
            if show_updates_in_terminal:
                print(f'\r{self.url}: Image {i+1}/{len(img_urls)}', end='')

        # here we print the same text we already printed to show that the chapter's downloaded, but with \n at the end to stop the output becoming all wonky after downloading a chapter
        print(f'\r{self.url}: Image {i + 1}/{len(img_urls)}', end='\n')

        # finally we return the images
        return ImageDownloads(img_bytes)

class Series:
    def __init__(self, url: str):
        self.url = url

    def get_chapter_urls(self) -> list[str]:
        '''Returns a list of the urls to all the chapters of a series as strings

        Example Code:
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

        # now the final final thing is returning the urls we just extracted
        return chapter_urls

    def download(self) -> SeriesImageDownloads:
        '''Gets every chapter of a series' images and returns them as a SeriesImageDownloads object
        This function will not save the images anywhere, instead call save on the SeriesImageDownloads object it returns

        Example Code:
        import os

        path_to_save_images_to = 'put/your/path/here'

        # making the series object
        c = Series('https://www.mangaread.org/manga/the-beginning-after-the-end/')

        # downloading the images
        img_bytes = c.download()'''
        # first we get all the urls for the chapters in the series
        chapter_urls = self.get_chapter_urls()

        # next we go through and download every chapter
        downloaded_chapters = []
        for chapter_url in chapter_urls:
            # the first step is making a chapter object for the chapter
            chapter_object = Chapter(chapter_url)

            # then we download it and add it to downloaded_chapters
            downloaded_chapters.append(chapter_object.download())

        # after that we bundle all the downloaded chapters together in a SeriesImageDownloads object
        bundled_chapters = SeriesImageDownloads(downloaded_chapters)

        # finally we return the downloaded chapters we just got
        return bundled_chapters

# all the functions here are for main.py
def download(url: str, output_path: str):
    '''Checks if the url works for this scraper, and if so downloads and saves the contents from the url, then returns True. Otherwise, it does nothing and returns False

    Example Code:
    from mangaread import download

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

            # next we download the images
            images = series_object.download()

            # finally we save them to the output path
            images.save(output_path)

            # then we return True so whatever is calling this knows it matched
            return True

        # this is for chapters
        elif chapter_regex.fullmatch(url):
            # since it matched, we give an indication it matched to the user
            print(f'Downloading {url}')

            # first we make an obejct for the chapter
            chapter_object = Chapter(url)

            # next we download the images
            images = chapter_object.download()

            # finally we save them to the output path
            images.save(output_path)

            # then we return True so whatever is calling this knows it matched
            return True

    else:
        # here we return false since it didn't match anything
        return False

def search(query: str, adult:  bool or None = None) -> list[SearchResult]:
    # first we turn the query into one we can later put into a url
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

    # first we get the div that has all the search results
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

    # finally we return the search results
    return search_results

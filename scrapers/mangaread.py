import os.path
import bs4
import requests
from common import SearchResult, sort_search_results, print_image_download_start, print_image_download_update, print_image_download_end
import re
import urllib.parse

class Chapter:
    def __init__(self, url: str):
        ''':param url: The url to the chapter'''
        self.url = url

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

    def download(self, output_path: str, show_updates_in_terminal: bool = True):
        '''Gets all the image urls for a chapter, then downloads them.
        This function will also save the images

        Example Code:
        from scrapers.mangaread import Chapter

        path_to_save_images_to = 'put/your/path/here'

        # making the chapter object
        chapter = Chapter('https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-224\')

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
        '''Gets every chapter of a series' images and saves them to output_path
        If output_path's basename is the name of the series, it will put all the chapters there, otherwise, it will create a folder to save the chapters to

        Example Code:
        from scrapers.mangaread import Series

        path_to_save_images_to = 'put/your/path/here'

        # making the series object
        series = Series('https://www.mangaread.org/manga/the-beginning-after-the-end/')

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

    # then the second to last step is feeding the search results through our own searching function
    # that function basically just sorts them all by how similar their names are to the query

    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the search results
    return sorted_search_results

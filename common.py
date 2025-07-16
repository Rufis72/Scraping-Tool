import difflib
import os
from urllib import parse
import requests

class SearchResult:
    '''This is the class for search results from manga websites
    Note: This class is mainly used for readability.

    Example Code:
    from common import SearchResult

    # these are all the values for the search result
    url = 'https://www.mangaread.org/manga/the-beginning-after-the-end/'
    name = 'The Beginning After the End'
    website_id = 'mangaread' # this is a specific ID for a scraper (in this case scrapers/mangaread.py)

    example_search_result = SearchResult(name, url, website_id)

    # you can then access those stored values as shown here:
    print(example_search_result.url) # outputs 'https://www.mangaread.org/manga/the-beginning-after-the-end/'
    print(example_search_result.name) # outputs 'The Beginning After the End'
    print(example_search_result.website_id) # outputs 'mangaread'

    # or you can just print the SearchResult object and it will format it nicely
    print(example_search_result) # outputs (this is sudo code) 'mangaread' + href_but_for_terminal_leading_to_mangaread's_website + ': ' + 'The Beginning After the End' + 'href_but_for_terminal_which_makes_the_name_lead_to_the_page_for_it's_series''

    '''

    def __init__(self, name: str, url: str, website_id: str):
        self.name = name
        self.url = url
        self.website_id = website_id

    def __str__(self) -> str:
        '''This function turn the search result into a string for basically debugging purposes
        It outputs this (this is sudo code) f'{SearchResult's_website_id_with_a_clickable_link_to_it's_url}: {SearchResult.name_with_a_clickable_link_to_SearchResult.url}' '''
        return f'{generate_text_with_link('https://' + parse.urlparse(self.url).hostname, self.website_id)}: {generate_text_with_link(self.url, self.name)}'

    def __repr__(self) -> str:
        return self.__str__()

class SharedSeriesClass:
    '''This is a base class for all series classes for scrapers.
    SharedSeriesClass already has a download method, so you just need to write a get_chapter_url method to get chapter urls.

    Example Code:

    # this should be a reference to the class, since the download method needs a reference
    your_chapter_class = Chapter # do not initialize the class here

    # this is if you don't want to alwasy have to include your chapter_object_reference in the download method
    def download(self, output_path):
        super.download(output_path, chapter_object_reference=your_chapter_class)'''
    def __init__(self, url: str):
        self.url = url

    def download(self, output_path: str, chapter_object_reference: type, show_updates_in_terminal: bool = True):
        '''This is the generic shared series class download function. It will call self.get_chapter_urls, then download them. If headers are passed in, it will use those when requesting the chapters
        This function is mainly for organizing where chapters should go, so it doesn't do any requests on it's own. It just gets the paths to where the chapters should saves them

        Example Code:
        from common import SharedSeriesClass

        # now we make a class with our own get_chapter_urls method
        class Series(SharedSeriesClass):
            """put a doc string here if you choose"""

            def __init__(self, url: str):
                super.__init__(url)

            def get_chapter_urls(self) -> str:
                """put some documentation here if you want"""
                # put your chapter-getting logic here

        path_to_save_images_to = 'put/your/path/here'

        # making the series object using the Series class we just defined
        series = Series('https://mangabuddy.com/the-beginning-after-the-end')

        # downloading the images
        series.download(output_path)
        :param output_path: The path where the images will be saved to
        :param chapter_object_reference: The reference to the Chapter object for this scraper
        :param headers: The headers used when requesting chapters'''
        # first we get all the urls for the chapters in the series
        chapter_urls = self.get_chapter_urls()

        # next we go through and download every chapter
        for i, chapter_url in enumerate(chapter_urls):
            # the first step is making a chapter object for the chapter
            chapter_object = chapter_object_reference(chapter_url)

            # then we download it and add it to downloaded_chapters
            # we also pass the output path
            chapter_object.download(os.path.join(output_path, chapter_object.get_name()), show_updates_in_terminal=show_updates_in_terminal)

    def get_chapter_urls(self, *args):
        '''Fetches a series' url and extracts the urls to that series' chapters

        Example Code:
        from scrapers.<your_scraper_here> import Series

        # making the series object
        series = Series('https://put.the/your/to/your/series/here/')

        # getting the chapter urls
        chapter_urls = Series.get_chapter_urls()
        :returns: A list of chapter urls as strings'''
        raise Exception(f'You need to make your own get_chapter_urls method!')
    
    
    def get_name(self) -> str:
        '''Attempts to extract the name of a series, if it fails it just returns the entire url, otherwise it returns the extracted name
        Warning: This code only does VERY basic trying to extract the name, so if your website doesn't have the name immediately after 'manga/' in the url, you shuold make your own version of this function

        Example Code:
        from common import SharedSeriesClass

        # making a series class using the SharedSeriesClass as it's super class
        class Series(SharedSeriesClass):
            def __init__(url):
                super().__init__(url)

            def get_img_urls():
                # put your code to extract image urls here

        # making the series object
        series_object = series('https://put.your/url/here)

        # printing the series' name
        print(series_object.get_series_name())'''
        # first, if the url has 'manga/' we just take whatever is inbetween the part after manga/ and the next slash as it's name
        if self.url.__contains__('manga/') and len(self.url.split('manga/')[1]) > 1:
            return self.url.split('manga/')[1].split('/')[0]

        # if the previous attempt didn't work, we just return the last part in the url
        else:
            return parse.urlparse(self.url).path.strip('/').split('/')[-1]

class SharedChapterClass:
    '''This is a base class for all chapter classes for scrapers.
    SharedChapterClass already has a download method, so you just need to write a get_chapter_url method to get chapter urls.
    You do need to make your own get_img_urls method'''

    def __init__(self, url: str):
        self.url = url

    def get_img_urls(self):
        '''Fetches a chapter and extracts the urls to that chapter's images

        Example Code:
        from scrapers.<your_scraper_here> import Chapter

        # initializing the chapter object
        chapter = Chapter('https://put.the/url/to/your/chapter/here/')

        # getting the image urls
        image_urls = Chapter.get_img_urls()
        :returns: A list of the urls to the images as strings'''
        raise Exception(f'You need to make your own get_img_urls method!')

    def download(self, output_path: str, show_updates_in_terminal: bool = True, image_headers: dict = None, add_host_to_image_headers: bool = False, replace_image_failed_error_with_warning: bool = False):
        '''The default download function for Chapters. It gets all the image urls for a chapter, then requests those images and saves them
        If the output paths's directory is the name of the chapter, it will save all it's images there, otherwise it will make a directory with the name of the chapter and save the images there

        Example Code:
        from common import SharedChapterClass

        path_to_save_images_to = '/put/your/path/here'

        # making the chapter object
        # make sure to include the scheme for the url
        chapter = Chapter('https://put.your/url/to/your/chapter/here')

        # downloading the images
        chapter.download(path_to_save_images_to)
        :param output_path: The path the images will be saved to
        :param show_updates_in_terminal: If updates should be shown in terminal when downloading
        :param image_headers: The headers used to request images
        :param add_host_to_image_headers: If the hostname should be added to headers under the header 'Host'
        '''
        # first we get all the img urls
        print(replace_image_failed_error_with_warning)
        img_urls = self.get_img_urls()

        # next we make a directory for the chapter (if we're not in it already, or it already exists)
        output_path = get_correct_output_path(output_path, self.get_name())

        # if enabled we print an update in terminal showing we've started the download
        if show_updates_in_terminal:
            print_image_download_start(self.url, len(img_urls))

        for i, img_url in enumerate(img_urls):
            # first we add the hostname to headers under 'Host' if enabled
            if add_host_to_image_headers:
                image_headers['Host'] = parse.urlparse(img_url).hostname

            # secondly we request the img
            img_response = requests.get(img_url)

            # next we make sure the request went through
            if img_response.status_code != 200:
                # we also store the status code in case we need to use it for an error message
                status_code_one = img_response.status_code
                # if it didn't, we request it one more time
                img_response = requests.get(img_url, headers=image_headers)

                # and if that still doesn't work, we raise an error unless replace_image_vailed_error_with_warning is toggled, then we print a warning instead
                if replace_image_failed_error_with_warning and show_updates_in_terminal and img_response.status_code != 200:
                    print(f'\033[91m Got status codes {status_code_one} and {img_response.status_code} when requesting \'{img_url}\'. It is highly recommended that you use another source, since downloading here may not get you all the images. This scraper has opted to replace errors with warnings, meaning this is expected behavior.\033[00m')
                # the elif is here because the first condition needs show updates in terminal, and replace image failed error with warning to be true, but if show updates in terminal isn't, it'll still raise an error even though told not to
                elif not replace_image_failed_error_with_warning and img_response.status_code != 200:
                    if img_response.status_code != 200:
                        raise Exception(
                            f'Got status codes {status_code_one} when requesting \'{img_url}\'. Then we retried getting the image, got status code {img_response.status_code}')

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


    def get_name(self) -> str:
        '''Attempts to extract the name of a chapter, if it fails it just returns the entire url, otherwise it returns the extracted name
        Warning: This code only does VERY basic trying to extract the name, so if your website doesn't have the name immediately after 'manga/' in the url, you shuold make your own version of this function

        Example Code:
        from common import SharedChapterClass

        # making a chapter class using the SharedChapterClass as it's super class
        class Chapter(SharedChapterClass):
            def __init__(url):
                super().__init__(url)

            def get_img_urls():
                # put your code to extract image urls here

        # making the chapter object
        chapter_object = Chapter('https://put.your/url/here)

        # printing the chapter's name
        print(chapter_object.get_chapter_name())'''
        # first we make a variable for the beautified name
        self.url = self.url

        # next if the url has 'manga/' we just take whatever is inbetween the part after manga/ and the next slash as it's name
        if self.url.__contains__('manga/') and len(self.url.split('manga/')[1].split('/')) > 1:
            return self.url.split('manga/')[1].split('/')[1]

        # if the previous attempt didn't work, we just return the last part in the url
        else:
            return parse.urlparse(self.url).path.strip('/').split('/')[-1]


def get_correct_output_path(output_path: str, name: str) -> str:
    '''If the output path's base name name equals name, then it returns output_path. Otherwise, it creates a directory inside the output_path directory with it's name being the name parameter, and returns that path'''
    if os.path.basename(output_path) == name:
        # here we make sure the directory exists, just in case
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        # now we return the output path
        return output_path

    # otherwise since we're not already in the output path, we make a sub directory for one if it doesn't exist, then return the path to it
    else:
        if not os.path.exists(os.path.join(output_path, name)):
            os.mkdir(os.path.join(output_path, name))
        return os.path.join(output_path, name)


def generate_text_with_link(uri, label=None) -> str:
    '''Returns a string that when printed in a modern terminal will show text that when clicked leads to a url
    Note: the uri must have a scheme for terminals to interpret it as a link ('http://' or 'https://')

    Example Code:
    from common import generate_text_with_link

    url = 'google.com'
    text = 'google'

    text = generate_text_with_link(url, text)
    :param uri: The url that the text will link to
    :param label: The text that will be shown
    '''
    if label is None:
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)

def sort_search_results(search_results: list[SearchResult], query: str) -> list[SearchResult]:
    '''Sorts all the passed in search results by how close their title is to the query

    Example Code:
    from scrapers.mangaread import search
    from common import sort_search_results

    # this is the query we'll be using to search for results
    query = 'The Beginning After the End'

    # first we search to get a list of SearchResults we can sort
    search_results = search(query)

    # this is sorting them
    sorted_search_results = sort_search_results(search_results, query)'''
    # first we define a variable to store our list of sorted results
    similarity_list = []

    # then we calculate similarity scores using a for loop
    for obj in search_results:
        score = difflib.SequenceMatcher(None, obj.name, query).ratio()
        similarity_list.append((obj, score))

    # Sort the list of tuples based on the similarity score
    similarity_list.sort(key=lambda x: x[1], reverse=True)

    # then we extract the objects from the sorted list of results, and we've done it!
    sorted_results = []
    for object, score in similarity_list:
        sorted_results.append(object)

    # finally we return the sorted results
    return sorted_results


def print_image_download_end(url: str, total_images: int) -> None:
    '''Clears the current line and print an image downloading update with a new line at the end

    Example Code:
    from common import print_image_download_end

    print_image_download_end('https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-1-the-end-of-the-tunnel/', 43)

    # that code would output this: '\rhttps://www.mangaread.org/manga/the-beginning-after-the-end/chapter-1-the-end-of-the-tunnel/: 43/43\n'
    :param url: The url to print an update for with the given data
    :param total_images: The first and second number in the progress indicator (total_images/total_images)'''
    print(f'\r{url}: {total_images}/{total_images}', end='\n')


def print_image_download_update(url: str, current_progress: int, total_images: int) -> None:
    '''Clears the current line and print an image downloading update with no new line at the end

    Example Code:
    from common import print_image_download_update

    print_image_download_update('https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-1-the-end-of-the-tunnel/', 3, 43)

    # that code would output this '\nhttps://www.mangaread.org/manga/the-beginning-after-the-end/chapter-1-the-end-of-the-tunnel/: 4/43'
    :param url: The url to print an update for with the given data
    :param total_images: The second number in the progress indicator (current_progress/total_images)
    :param current_progress The first number in the progress indicator (current_progress/total_images) One is added to this to make it say 0/n when one image has been downloaded'''
    print(f'\r{url}: {current_progress + 1}/{total_images}', end='')


def print_image_download_start(url: str, total_images: int) -> None:
    '''Prints an image downloading update

    Example Code:
    from common import print_image_download_start

    print_image_download_start('https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-1-the-end-of-the-tunnel/', 43)
    # this would output 'https://www.mangaread.org/manga/the-beginning-after-the-end/chapter-1-the-end-of-the-tunnel/: 0/43' (no \n at the end)

    :param url: The url to print an update for with the given data
    :param total_images: The second number in the progress indicator (0/total_images)'''
    print(f'\r{url}: 0/{total_images}', end='')

def construct_chapter_not_found_image(chapter_urls: list[str], input_chapter: int):
    '''Returns a string like this:

    <inputted chapter here> wasn't a valid chapter. There are only <amount of chapters> chapters, these are the available chapters to download. To download one, type the number before the ':'
    0: <url here>
    1: <url here>
    etc

    Example Code:

    chapter_urls_list = ['google.com', 'duckduckgo.com', 'bing.com', 'yahoo.com']

    print(construct_chapter_not_found_image(chapter_urls, 9999999))
    :param chapter_urls: The list of chapter urls
    :param input_chapter: The invalid input chapter the user gave'''
    url_list_dialog = ''
    for i, chapter_url in enumerate(chapter_urls):
        url_list_dialog += f'{i}: {chapter_url}\n'

    # constructing the full dialog
    full_dialog = f'{url_list_dialog}{input_chapter} wasn\'t a valid chapter. There are only {len(chapter_urls)} chapters. These are the available chapters to download. To download one, type the number before the \':\'.\n'

    # now we return the dialog
    return full_dialog
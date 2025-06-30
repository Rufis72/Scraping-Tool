import difflib
import sys
from urllib import parse

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
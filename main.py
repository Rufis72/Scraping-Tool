import argparse
import os
from scrapers import mangaread
from common import SearchResult, generate_text_with_link
import typing


def get_scraper_mappings() -> dict[str, dict]:
    '''This returns the mappings of a scraper's name to it's download function, search function, and everything else related to it'''
    return {
        'mangaread': {
            'url': 'mangaread.org',
            'download_function': mangaread.download,
            'search_function': mangaread.search,
            'type': 'manga'
        }
    }

def download(url: str, output_path: str) -> bool:
    '''This function goes through every scraper and checks if they can download the url
    It returns True if it could find something, otherwise it returns False'''
    # here we go through all the values of every scraper, so we can use that download_function, and see if it works
    for scraper_data in get_scraper_mappings().values():
        # here we save the download_function of the current scraper to a variable for readability
        current_download_function = scraper_data.get('download_function')

        # now we call the function
        # if it works (return True) we return True to let whatever is running this function know it worked, otherwise we go onto the next scraper function
        if current_download_function(url, output_path):
            return True

    # here we return False since it only could've gotten here if none of the download functions worked
    return False

def search(query: str, adult: bool or None) -> list[SearchResult]:
    '''Searches the given query on as many sites as possible'''
    # here we go through every scraper, and call its search function
    # but first before we do that, we declare a variable to store the search results
    search_results = []

    # now we actually do all the searching
    for scraper in get_scraper_mappings().values():
        # we save the search function to a variable for readability
        search_function = scraper.get('search_function')

        # now we call the search function, and append it's result to our list of search results
        # we only take the top result, so that the list of results doesn't become overwhelming
        search_result = search_function(query, adult)
        # we check if there are any search results, otherwise we don't add it to search results
        if search_result:
            search_results.append(search_function(query, adult)[0])

    # finally we return the search_results
    return search_results

def main(args):
    '''Does all the downloading stuff with the passed in args'''
    # first we figure out if the user wants to search something
    # this is simple enough, since we just check if something has been passed to --search
    if args.search:
        # first we get the search results
        search_results = search(args.text, args.adult)

        # next, we construct the search results stuff we'll print
        search_results_user_prompt = 'Please enter the number of the manga you\'d like to download'
        # here we go through every search result and add it to the strings we're about to print
        for i, search_result in enumerate(search_results):
            # first we make a new line for every search result
            search_results_user_prompt += '\n'

            # next we add the number and data for the search result
            search_results_user_prompt += f'{i}: {generate_text_with_link(search_result.url, search_result.name)}'

        # we add a new line character here, since the string would be missing one otherwise
        search_results_user_prompt += '\n'

        # if there were no search results, we change the string, and end the function
        if not search_results:
            print(f'No results found for query \'{args.text}\'')
            return None

        # since there were search results, we get the input from the user of which one to download
        one_to_download = input(search_results_user_prompt)

        # now, we download that
        # first we get the download function for that website
        # this mess of a line boils down to getting the website that the result was from, then getting that website's download function
        download_function = get_scraper_mappings().get(search_results[int(one_to_download)].website).get('download_function')

        # now we check if -o flag has an output path, or if we should just save everything in the working directory
        if args.o:
            output_path = args.o
        else:
            output_path = os.getcwd()

        # now we finally download the series
        download_function(search_results[int(one_to_download)].url, output_path)

    # this is for just downloading a url
    else:
        # we can basically just call download, and have it do it all for us
        # the only thing we have to do is get the output path, which is simple
        # if there is no output path specified, it's the working directory, otherwise, it's whatever was specified
        if args.o:
            output_path = args.o
        else:
            output_path = os.getcwd()
        download(args.text, output_path)



if __name__ == '__main__':
    '''This does all the handling of the arguments when run from the command line'''
    # first we declare a parser to parse the arguments
    # the description is the description that will appear near the top when -h or --help is called
    parser = argparse.ArgumentParser(description='Scraping Tool is a scraper with a cli coded in python3. It\'s main use is scraping manga, webtoons, and some other misc items')

    # here we add all the optional arguments
    # these will show up when -h or --help is called
    parser.add_argument('-o', type=str, help='The output path where the extracted data will be saved')
    parser.add_argument('--search', action='store_true', help='If the text entered should be treated as a query or not')
    parser.add_argument('--adult', type=bool, help='If search results should include adult content')

    # here we do the positional arguments like the url
    parser.add_argument('text', type=str, help='The url to be scraped and downloaded')

    # next we parse the arguments
    args = parser.parse_args()

    # finally we call the main function with all the args we just got
    main(args)
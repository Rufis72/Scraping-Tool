import argparse
import os
from scrapers import mangaread, natomanga, mangabuddy, webtoons
from common import SearchResult, generate_text_with_link, sort_search_results
from common import construct_chapter_not_found_image


def get_scraper_mappings() -> dict[str, dict[str, str or callable]]:
    '''This returns the mappings of a scraper's name to it's download function, search function, and everything else related to it'''
    return {
        'mangaread': {
            'url': 'mangaread.org',
            'series_class_reference': mangaread.Series,
            'chapter_class_reference': mangaread.Chapter,
            'search_function': mangaread.search,
            'download_chapter_function': mangaread.download_chapter,
            'identify_url_type_function': mangaread.identify_url_type
        },
        'manganato': {
            'url': 'natomanga.com',
            'series_class_reference': natomanga.Series,
            'chapter_class_reference': natomanga.Chapter,
            'search_function': natomanga.search,
            'download_chapter_function': natomanga.download_chapter,
            'identify_url_type_function': natomanga.identify_url_type

        },
        'mangabuddy': {
            'url': 'mangabuddy.com',
            'series_class_reference': mangabuddy.Series,
            'chapter_class_reference': mangabuddy.Chapter,
            'search_function': mangabuddy.search,
            'download_chapter_function': mangabuddy.download_chapter,
            'identify_url_type_function': mangabuddy.identify_url_type
        },
        'webtoons': {
            'url': 'webtoons.com',
            'series_class_reference': webtoons.Series,
            'chapter_class_reference': webtoons.Chapter,
            'search_function': webtoons.search,
            'download_chapter_function': webtoons.download_chapter,
            'identify_url_type_function': webtoons.identify_url_type
        }
    }

def download_chapter(series_url: str, chapter_num: int, output_path: str):
    '''Donwloads the chapter_numth chapter of a series. If the chapter number does not exist, or is invalid, it will give the user dialog to pick another option

    Example Code:

    from main import download_chapter

    download_chapter('https://mangabuddy.com/the-beginning-after-the-end', 224)
    :param series_url: The url of the series
    :param chapter_num: The index of the chapter to be downloaded
    :param output_path: Where the chapter's images will be saved'''
    # first we get the scraper for the url's functions
    for scraper in get_scraper_mappings().values():
        if scraper.get('identify_url_type_function')(series_url) != None:
            scraper_functions = scraper

    # after that, we make sure we got a scraper
    try:
        # this would raise an error if the variable didn't exist
        scraper_functions.get('')
    except:
        # here we say we couldn't find a scraper for that url
        print(f'No scrapers matched the url \'{series_url}\'')
        return False


    # next we make a series object for the series using the scraper's series class we just got
    series_object = scraper_functions.get('series_class_reference')(series_url)

    # next we get all the chapter urls for that series
    chapter_urls = series_object.get_chapter_urls()

    # after that we check if the chapter_num is a valid index for the chapter_urls (aka it's not 99999 and there's only 7 chapters)
    try:
        # this does two things. First it checks if the chapter_num is valid, then it gets the url to the chapter we're downloading
        chapter_to_download_url = chapter_urls[chapter_num]

    except:
        # checking if there's no chapters just in case
        if len(chapter_urls) == 0:
            print(f'Sorry! \'{series_url}\' doesn\'t seem to have any chapters!')

        # now we get the input from the user for what chapter num they want to download
        new_user_chapter_num = int(input(construct_chapter_not_found_image(chapter_urls, chapter_num)))

        # then the last step before downloading is getting the url corresponding to that number
        chapter_to_download_url = chapter_urls[new_user_chapter_num]


    # now we download the chapter
    # even if the chapter_num wasn't valid, it'll still save the new chapter_url to chapter_to_download_url
    scraper_functions.get('chapter_class_reference')(chapter_to_download_url).download(output_path)
    # checking if we got a scraper



def download(url: str, output_path: str) -> bool:
    '''Checks if the url works for this scraper, and if so downloads and saves the contents from the url, then returns True. Otherwise, it does nothing and returns False

    Example Code:
    from main import download

    download('https://mangabuddy.com/the-beginning-after-the-end') # this will return True and download it
    :param url: The url we are checking if matches, and if so downloading
    :param output_path: The output path to save the downloaded images to'''
    # first we go through, and get the scraper it's for, and it's type
    for scraper in get_scraper_mappings().values():
        # what we do is identify the url type, then if it's a str, we know it works for that scraper!
        url_type = scraper.get('identify_url_type_function')(url)
        scraper_functions = scraper
        # if it worked, we break out of the loop
        if type(url_type) == str:
            break

    # here we check if we should return False because no scrapers seemed to be able to download that url
    if url_type == None:
        return False

    # this is downloading logic for a series
    if url_type == 'series':
        # since it matched, we give an indication it matched to the user
        print(f'Downloading {url}')

        # first we make an object for the series
        series_object = scraper_functions.get('series_class_reference')(url)

        # after that we make the directory for the series. (if we're not already in it)
        # if we are already in the directory for the series directory, the following code will be False and nothing will happen
        if os.path.basename(output_path) != url.strip('/').split('/')[-1]:
            # if the directory for the series directory doesn't exist, we make it
            if not os.path.exists(os.path.join(output_path, url.strip('/').split('/')[-1])):
                os.mkdir(os.path.join(output_path, url.strip('/').split('/')[-1]))
            # now we just change the output path to the new directory for the series one so we can just pass output_path to the download function either way
            output_path = os.path.join(output_path, url.strip('/').split('/')[-1])

        # next we download the images
        # the download function also saves them, so we don't have to worry about that
        series_object.download(output_path)

        # then we return True so whatever is calling this knows it matched
        return True

    # this is for chapters
    elif url_type == 'chapter':
        # since it matched, we give an indication it matched to the user
        print(f'Downloading {url}')

        # first we make an object for the chapter
        chapter_object = scraper_functions.get('chapter_class_reference')(url)

        # next we download the images
        chapter_object.download(output_path)

        # then we return True so whatever is calling this knows it matched
        return True

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

    # next we sort the search results to make sure the best are at the top
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the search_results
    return sorted_search_results

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
            search_results_user_prompt += f'{i}: {generate_text_with_link(search_result.url, search_result.name)} ({get_scraper_mappings().get(search_result.website_id).get('url')})'

        # we add a new line character here, since the string would be missing one otherwise
        search_results_user_prompt += '\n'

        # if there were no search results, we alert the user and end the script
        if not search_results:
            print(f'No results found for query \'{args.text}\'')
            return None

        # since there were search results, we get the input from the user of which one to download
        one_to_download = input(search_results_user_prompt)

        # now, we download that
        # first we get the download function for that website
        # this mess of a line boils down to getting the website that the result was from, then getting that website's download function
        download_function = get_scraper_mappings().get(search_results[int(one_to_download)].website_id).get('download_function')

        # now we check if -o flag has an output path, or if we should just save everything in the working directory
        if args.o:
            output_path = args.o
        else:
            output_path = os.getcwd()

        # before we download it, we've gotta check if we should be downloading a specific chapter specified by the --chapter flag
        if args.chapter:
            # now we've gotta get the chapter_download_function too
            # this mess of a line boils down to getting the website that the result was from, then getting that website's download function
            chapter_download_function = (get_scraper_mappings().get(search_results[int(one_to_download)].website_id)
                                 .get('download_chapter_function'))

            # now we use that function to download the chapter
            chapter_download_function(search_results[int(one_to_download)].url, args.chapter, output_path)
        else:
            # since we're not downloading a specific, chapter we download the entire series
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

        # here we check if we should be downloading a specific chapter
        if args.chapter:
            download_chapter(args.text, args.chapter, output_path)

        # otherwise we just download as usual
        else:
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
    parser.add_argument('--chapter', type=int, help='The chapter index to be downloaded. Works with searching, and downloading a series. It will download that index from the list of chapter urls when downloading')

    # here we do the positional arguments like the url
    parser.add_argument('text', type=str, help='The url to be scraped and downloaded')

    # next we parse the arguments
    args = parser.parse_args()

    # finally we call the main function with all the args we just got
    main(args)
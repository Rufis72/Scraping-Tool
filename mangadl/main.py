#!/usr/bin/env python3
import os
from mangadl.scrapers import mangaread, natomanga, mangabuddy, webtoons, mangatown, onemanga, bato, tapas, comix, mangadex
from mangadl.common import SearchResult, generate_text_with_link, sort_search_results
from mangadl.common import construct_chapter_not_found_image
from mangadl.common import get_correct_output_path
import mangadl.common
import re
import difflib
from mangadl.formatters.pdf import manga as pdf_manga, webtoon as pdf_webtoon


def get_scraper_mappings() -> dict[str, dict[str, str or callable or type]]:
    '''This returns the mappings of a scraper's name to it's download function, search function, and everything else related to it'''
    return {
        'mangaread': {
            'url': mangaread.urls[0],
            'series_class_reference': mangaread.Series,
            'chapter_class_reference': mangaread.Chapter,
            'search_function': mangaread.search,
        },
        'manganato': {
            'url': natomanga.urls[0],
            'series_class_reference': natomanga.Series,
            'chapter_class_reference': natomanga.Chapter,
            'search_function': natomanga.search,

        },
        'mangabuddy': {
            'url': mangabuddy.urls[0],
            'series_class_reference': mangabuddy.Series,
            'chapter_class_reference': mangabuddy.Chapter,
            'search_function': mangabuddy.search,
        },
        'webtoons': {
            'url': webtoons.urls[0],
            'series_class_reference': webtoons.Series,
            'chapter_class_reference': webtoons.Chapter,
            'search_function': webtoons.search,
        },
        'mangatown': {
            'url': mangatown.urls[0],
            'series_class_reference': mangatown.Series,
            'chapter_class_reference': mangatown.Chapter,
            'search_function': mangatown.search,
        },
        '1manga': {
            'url': onemanga.urls[0],
            'series_class_reference': onemanga.Series,
            'chapter_class_reference': onemanga.Chapter,
            'search_function': onemanga.search,
        },
        'bato': {
            'url': bato.urls[0],
            'series_class_reference': bato.Series,
            'chapter_class_reference': bato.Chapter,
            'search_function': bato.search,
        },
        'tapas': {
            'url': tapas.urls[0],
            'series_class_reference': tapas.Series,
            'chapter_class_reference': tapas.Chapter,
            'search_function': tapas.search,
        },
        'comix': {
            'url': comix.urls[0],
            'series_class_reference': comix.Series,
            'chapter_class_reference': comix.Chapter,
            'search_function': comix.search,
        },
        'mangadex': {
            'url': mangadex.urls[0],
            'series_class_reference': mangadex.Series,
            'chapter_class_reference': mangadex.Chapter,
            'search_function': mangadex.search,
        },
    }


def get_scraper_function_mappings_by_url(url: str) -> dict[str, str or callable] or None:
    '''Gets the scraper for a given url, and returns that scrapers functions'''
    # looping through every scraper
    for scraper_name in get_scraper_mappings().keys():
        # checking if the url works for that scraper
        if identify_url_type(scraper_name, url) != None:
            # returning the scraper's functions
            return get_scraper_mappings().get(scraper_name)

def get_scraper_name_by_url(url) -> str or None:
    '''Gets the name of a scraper via a url and returns it
    :param url: The url to get the scraper name by
    :returns: Either the name of the scraper, or None if nothig matched'''
    # looping through every scraper
    for scraper_name in get_scraper_mappings().keys():
        # checking if the url works for that scraper
        if identify_url_type(scraper_name, url) != None:
            # returning the scraper's functions
            return scraper_name


def identify_url_type(scraper_name: str, url: str) -> str or None:
    '''Identifys the type of a url with a specific scraper's regex for identifying urls

    Example Code:
    from main import identify_url_type

    # the following code would print 'chapter' since it's a chapter
    print(identify_url_type('webtoons', 'https://www.webtoons.com/en/action/hero-killer/episode-1/viewer?title_no=2745&episode_no=1'))
    :returns: Either 'chapter', 'series', or None depending on if the regex for a specific scraper's chapter or series match
    :param scraper_name: The name of the scraper in get_scraper_mappings
    :param url: The url to be identified'''
    # first we get the functions and classes for the given scraper
    scraper_functions = get_scraper_mappings().get(scraper_name)

    # then we get the chapter regex and series regex
    chapter_regex = re.compile(scraper_functions.get('chapter_class_reference').regex)
    series_regex = re.compile(scraper_functions.get('series_class_reference').regex)

    # then we try to match our url against those regexs
    if chapter_regex.fullmatch(url):
        return 'chapter'
    elif series_regex.fullmatch(url):
        return 'series'
    # since it didn't match either, we return None
    else:
        return None


def download_chapter_by_chapter_num(series_url: str, chapter_num: int, output_path: str, redownload: bool, show_updates_in_terminal: bool = True):
    '''Donwloads the chapter_numth chapter of a series. If the chapter number does not exist, or is invalid, it will give the user dialog to pick another option

    Example Code:

    from main import download_chapter

    download_chapter_by_chapter_num('https://mangabuddy.com/the-beginning-after-the-end', 224)
    :param series_url: The url of the series
    :param chapter_num: The index of the chapter to be downloaded
    :param output_path: Where the chapter's images will be saved
    :param redownload: If the chapter should be redownloaded, even if already downloaded'''
    # first we get the scraper for the url's functions
    scraper_functions = get_scraper_function_mappings_by_url(series_url)

    # after that, we make sure we got a scraper
    if scraper_functions == None:
        print(f'No scrapers matched the url \'{series_url}\'')
        return None

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
    scraper_functions.get('chapter_class_reference')(chapter_to_download_url).download(output_path, show_updates_in_terminal, redownload=redownload)


def download_chapters(series_url : str, starting_chapter_num: int, ending_chapter_num: int or None, output_path: str, redownload: bool, show_updates_in_terminal: bool = True):
    '''Downloads multiple chapters from a series via it's series_url
    :param series_url: The url to the series
    :param starting_chapter_num: The starting chapter to be downloaded from
    :param ending_chapter_num: The ending chapter to be downloaded from
    :param output_path: The path where the chapters and the images will be saved
    :param redownload: If a chapter should be redownloaded, even if already downloaded'''
    # first we get the scraper were gonna use for the url's functions
    scraper_functions = get_scraper_function_mappings_by_url(series_url)

    # then we make a series object
    series_object = scraper_functions.get('series_class_reference')(series_url)

    # giving an update for what we're doing (if enabled)
    if show_updates_in_terminal:
        print(f'Getting chapter urls for \'{series_url}\'')

    # after that we get the chapter urls
    chapter_urls = series_object.get_chapter_urls()

    # then we get the list of the chapter url's we're gonna download
    # if the user passed in something like 1- or 4:, then we download chapters 4-[end_of_list]
    # the way we do that is if ending_chapter_num is None, we set it to len(chapter_urls) - 1
    if ending_chapter_num == None:
        ending_chapter_num = len(chapter_urls) - 1

    chapter_urls_to_download = chapter_urls[int(starting_chapter_num):int(ending_chapter_num)+1]

    # after that we make a directory (if we're not already in it) for the series
    output_path = get_correct_output_path(output_path, series_object.get_name())

    # finally we just use main.py's download function to download all the chapters
    # we also pass the chapter num we're downloading for progress update reasons (the '(chapter n/len(chapters))' part)
    for i, chapter_url_to_download in enumerate(chapter_urls_to_download):
        download_chapter(chapter_url_to_download, output_path, redownload, show_updates_in_terminal, i + 1, len(chapter_url_to_download))


def download_series(url: str, output_path: str, redownload: bool, show_updates_in_terminal: bool = True) -> bool:
    '''Downloads a series from it's url. Returns True if the url could be downloaded, otherwise returns False

    Example Code:
    from main import download_series

    download_series('https://mangabuddy.com/the-beginning-after-the-end') # this will return True and download it
    :param url: The url we are checking if matches, and if so downloading
    :param output_path: The output path to save the downloaded images to
    :param redownload: If a chapter should be redownloaded, even if already downloaded
    :param show_updates_in_terminal: If we should show updates in the terminal'''
    # first we go through all the scrapers, and get the scraper the url works for (if any)
    scraper_name = get_scraper_name_by_url(url)
    # then we get that scraper's functions via it's name
    scraper_functions = get_scraper_mappings().get(scraper_name)

    # after that, we make sure we got a scraper
    if scraper_functions == None:
        if show_updates_in_terminal:
            print(f'No scrapers matched the url \'{url}\'')
        return False

    # since it matched, we give an indication it matched to the user (if enabled)
    if show_updates_in_terminal:
        print(f'Downloading {url}')

    # first we make an object for the series
    series_object = scraper_functions.get('series_class_reference')(url)
    # after that we make the directory for the series. (if we're not already in it) Then we save that as our new output path
    # the first step to doing that is getting the name of our series
    series_name = series_object.get_name()

    # now we get the correct output_path with common.py's get_correct_output_path function
    output_path = get_correct_output_path(output_path, series_name)

    # next we download the images
    # the download function also saves them, so we don't have to worry about that
    series_object.download(output_path, show_updates_in_terminal=show_updates_in_terminal, redownload=redownload)

    # then we return True so whatever is calling this knows it matched
    return True


def download_chapter(url: str, output_path: str, redownload: bool, show_updates_in_terminal: bool = True, chapter_number: int = 1, chapter_count = 1) -> bool:
    '''Downloads a chapter/episode from it's url. Returns True if the url could be downloaded, otherwise returns False

    Example Code:
    from main import download_chapter

    download_chapter('https://mangabuddy.com/the-beginning-after-the-end/chapter-225') # this will return True and download it
    :param url: The url we are checking if matches, and if so downloading
    :param output_path: The output path to save the downloaded images to
    :param redownload: If a chapter should be redownloaded, even if already downloaded
    :param show_updates_in_terminal: If we should show updates in the terminal'''
    # first we go through all the scrapers, and get the scraper the url works for (if any)
    scraper_name = get_scraper_name_by_url(url)
    # then we get that scraper's functions via it's name
    scraper_functions = get_scraper_mappings().get(scraper_name)

    # after that, we make sure we got a scraper
    if scraper_functions == None:
        if show_updates_in_terminal:
            print(f'No scrapers matched the url \'{url}\'')
        return False

    # since it matched, we give an indication it matched to the user (if enabled)
    if show_updates_in_terminal:
        print(f'Downloading {url}')

    # first we make an object for the chapter
    chapter_object = scraper_functions.get('chapter_class_reference')(url)

    # next we download the images
    chapter_object.download(output_path, show_updates_in_terminal=show_updates_in_terminal, chapter_number=chapter_number, chapter_count=chapter_count, redownload=redownload)

    # then we return True so whatever is calling this knows it matched
    return True


def download_generic(url: str, output_path: str, redownload: bool, show_updates_in_terminal: bool = True) -> bool:
    '''Downloads a url, and identifys if it's a chapter/episode or series. Returns True if the url could be downloaded, otherwise returns False

    Example Code:
    from main import download_chapter

    download_chapter('https://mangabuddy.com/the-beginning-after-the-end/chapter-225') # this will return True and download it
    :param url: The url we are checking if matches, and if so downloading
    :param output_path: The output path to save the downloaded images to
    :param redownload: If a chapter should be redownloaded, even if already downloaded
    :param show_updates_in_terminal: If we should show updates in the terminal'''
    # getting a scraper that works for the url (this is required for identifying the url type)
    scraper_name = get_scraper_name_by_url(url)

    # returning False and telling the user (if enabled) that no scraper matched the given url
    if scraper_name == None:
        if show_updates_in_terminal:
            print(f'No scrapers matched the url \'{url}\'')
        return False

    # identifying the url type
    url_type = identify_url_type(scraper_name, url)

    # downloading the url with it's correct function
    # we return the output of the download function, since those also return True if it was successful, and False if it wasn't.
    if url_type == 'chapter':
        return download_chapter(url, output_path, redownload, show_updates_in_terminal)
    elif url_type == 'series':
        return download_series(url, output_path, redownload, show_updates_in_terminal)
    # otherwise we return false, and tell the user that there should've been something downloaded, but wasn't
    # it should've been caught when we got the scraper function, and nothing should've been found
    # since if we were able to get a scraper, that means either the series or chapter regex matched
    # meaning that it was identified as either a chapter or series earlier, but wasn't from identify_url_type
    else:
        if show_updates_in_terminal:
            print('Some went wrong when downloading that URL that shouldn\'t have happened. Please create an issue on the github, and say to refer to the comments in main.download_generic after the downloading logic for chapters and serieses. (That has a more in depth explination of the error)')
        return False

    


def search(query: str, adult: bool or None, results_per_website: int = 1) -> list[SearchResult]:
    '''Searches the given query on as many sites as possible'''
    # here we go through every scraper, and call its search function
    # but first before we do that, we declare a variable to store the search results
    search_results = []

    # now we actually do all the searching
    for scraper in get_scraper_mappings().values():
        # we save the search function to a variable for readability
        search_function = scraper.get('search_function')

        # we use try here in case we get an error around getting an error code when requesting the website
        try:
            # now we call the search function, and append it's result to our list of search results
            # we only take the top result, so that the list of results doesn't become overwhelming
            search_result = search_function(query, adult)
            
            # adding however many results we're supposed to add per website
            # the min is there so we don't try and add index 17 of a list with a length of 6
            # that also means we don't have to check if something has a length of 0, since then the for loop will just go in range(0)
            for i in range(min(results_per_website, len(search_result))):
                search_results.append(search_function(query, adult)[i])
        except Exception as e:
            print(e)
            #print(f'Got error with text: \'{e}\' when searching on scraper with the url {scraper.get('url')}')

    # next we sort the search results to make sure the best are at the top
    sorted_search_results = sort_search_results(search_results, query)

    # finally we return the search_results
    return sorted_search_results

def format(args):
    '''The function for handling the subcommand format'''
    # giving a warning that the format type defaulted to manga if none was given (if giving warnings is enabled)
    if args.content_format == None:
        if not args.disable_warnings:
            print('No content type was given for formatting, meaning it will default to formatting the content as manga. To format a webtoon pass \'--content-format webtoon\'')
        args.content_type = 'manga'

    # a dict for the different imports for formatting, to avoid a ton of if statements
    format_imports = {
        'pdf': {
            'manga': { # this section is for chapters vs whole series, as determined by is_series.
                True: pdf_manga.PDFMangaSeries,
                False: pdf_manga.PDFMangaChapter,
            },
            'webtoon': {
                True: pdf_webtoon.PDFWebtoonSeries,
                False: pdf_webtoon.PDFWebtoonChapter,
            },
        },
    }

    # attempting to infer the file format from -o if none was given (so if -o is ~/output/file.pdf for example)
    # if -o was a directory, then we raise an error
    if args.file_format == None:
        # trying to get the filetype
        if not os.path.isdir(args.output):
            args.file_format = os.path.splitext(args.output)[1]

        # if it wasn't able to be inferred, then we raise an error
        else:
            raise Exception(f'No file format for the output file(s) was passed, and none was able to be inferred from -i (\'{args.output}\'). To specify the file format, pass the file format as --file-format (ex \'--file-format pdf\'), or specify it in -o with something like \'~/output/file.pdf\'')

    # attempting to figure out if the data to be formatted is a serie or not if --is-series was not passed
    if not args.is_series:
        # what we basically check is if the directory has images in it
        if len([file for file in os.listdir(args.input) if file.lower().endswith(common.image_file_extensions_with_periods)]) > 0:
            args.is_series = False
        else:
            args.is_series = True

        # warning the user we inferred it, and telling them how to disable the warning & how to set --is-series
        if not args.disable_warnings:
            print(f'--is-series was not passed, so we inferred the content {({True: 'was a series', False: 'was a chapter/episode'}.get(args.is_series))}. To manually set this, pass --is-series (true/false), or to disable this and other warnings pass --disable-warnings')
        
    # raising an error if the file format we ended up with is unrecognized
    if format_imports.get(args.file_format.lower().lstrip('.')) == None:
        raise Exception(f'Formatting \'{args.file_format}\' files is unsupported. The supported file types are: \n{', '.join(format_imports.keys())}')

    # if it's a series, and we're formatting into multiple files, we check if the output path is to a directory
    if not args.chapters_per_file is None and (not os.path.exists(args.output) or not os.path.isdir(args.output)):
        raise Exception(f'The specificed output path \'({args.output})\' is not to a directory, which is required when formatting a set amount of chapters per file. (When --chapters-per-file is passed)')


    # now we use that dict to get the class we're using for formatting
    formatting_class = format_imports.get(args.file_format.lower().lstrip('.')).get(args.content_type).get(args.is_series)

    # now we initialize the object
    # if -i wasn't passed, we default to the current directory
    if args.input == None:
        args.input = os.getcwd
    formatting_object = formatting_class(args.input)

    # otherwise, we set series_name to '' if it wasn't passed
    if args.series_name == None:
        args.series_name = ''

    # now we format it
    # there's different logic for chapter/episodes and series
    # for series
    if args.is_series:
        formatting_object.format(args.output, args.chapters_per_file, args.chapter_naming_scheme, args.series_name)
    # for chapter/episodes
    else:
        formatting_object.format(args.output)


def download(args):
    '''Does all the downloading stuff with the passed in args'''
    # first we check if the user wants to list all valid website IDs
    if args.list_ids:
        print('\n'.join(get_scraper_mappings().keys()))

    # replacing : to - for -c and --chapters so you can do 1:20 or 1-20
    if args.chapter:
        args.chapter = args.chapter.replace(':', '-')

    # since they didn't want to list valid website IDs, we figure out if the user wants to search something
    # this is simple enough, since we just check if something has been passed to --search
    if args.search:
        # first we get the search results
        # if it's a meta search (searching all websites) we use the search function
        # otherwise we just use the scraper's search function directly
        if args.website:
            # here we check if the given website id is valid
            if get_scraper_mappings().get(args.website) == None:
                # now we tell the user that it wasn't valid, and how to get a list of them
                print(f'\'{args.website}\' wasn\'t a valid website ID. To see all valid website IDs run:\nmangascraper --list-ids')
                return
            # we try here in case we get an error
            search_results = get_scraper_mappings().get(args.website).get('search_function')(args.search, args.adult)
        else:
            search_results = search(args.search, args.adult, args.count)

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
            print(f'No results found for query \'{args.search}\'')
            return None

        # since there were search results, we get the input from the user of which one to download
        one_to_download = input(search_results_user_prompt)

        # finally, we download the chosen search result
        # first we check if -o flag has an output path, or if we should just save everything in the working directory
        if args.output:
            output_path = args.output
        else:
            output_path = os.getcwd()

        # before we download it, we've gotta check if we should be downloading a specific chapter specified by the --chapter flag (or -c)
        if args.chapter:
            # then we check if there's a dash (if we should download multiple chapters, but not the whole series
            if args.chapter.__contains__('-'):
                download_chapters(search_results[int(one_to_download)].url, int(args.chapter.split('-')[0]) - 1, int(args.chapter.split('-')[1]) - 1 if args.chapter.split('-')[1] != '' else None, output_path, args.redownload)
            # just downloading one chapter
            else:
                download_chapter_by_chapter_num(search_results[int(one_to_download)].url, int(args.chapter), output_path, args.redownload)
        else:
            # since we're not downloading a specific, chapter we download the entire series
            download_series(search_results[int(one_to_download)].url, output_path, args.redownload)

    # this is for just downloading a url
    elif args.text:
        # we can basically just call download, and have it do it all for us
        # the only thing we have to do is get the output path, which is simple
        # if there is no output path specified, it's the working directory, otherwise, it's whatever was specified
        if args.output:
            output_path = args.output
        else:
            output_path = os.getcwd()

        # here we check if we should be downloading a specific chapter
        if args.chapter:
            # then we check if there's a dash (if we should dowpnload multiple chapters, but not the whole series
            if args.chapter.__contains__('-'):
                download_chapters(args.text, int(args.chapter.split('-')[0]) - 1, int(args.chapter.split('-')[1]) - 1 if args.chapter.split('-')[1] != '' else None, output_path, args.redownload)
            # just downloading one chapter
            else:
                download_chapter_by_chapter_num(args.text, int(args.chapter), output_path, args.redownload)

        # otherwise we just download as usual
        else:
            download_generic(args.text, output_path, args.redownload)
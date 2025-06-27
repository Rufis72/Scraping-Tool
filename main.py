import argparse
import os
from scrapers import mangaread

def main(args):
    '''Does all the downloading stuff with the passed in args'''
    # first thing is getting the url from the args
    url = args.text

    # next we go through all the scraper's download functions and find one that works for the given url
    # this is the variable with all the download functions
    scraper_download_functions = [
        mangaread.download # this one is for mangaread.org
    ]

    # here we get the output path if none were specified
    if args.o:
        # this is for if it is, then we just get it from args
        output_path = args.o
    else:
        # otherwise we use the current working directory
        output_path = os.getcwd()

    # and this is the code to actually go through and find a matching url for a scraper
    for scraper_download_function in scraper_download_functions:
        scraper_download_function(url, output_path)



if __name__ == '__main__':
    '''This does all the handling of the arguments when run from the command line'''
    # first we declare a parser to parse the arguments
    # the description is the description that will appear near the top when -h or --help is called
    parser = argparse.ArgumentParser(description='Scraping Tool is a scraper with a cli coded in python3. It\'s main use is scraping manga, webtoons, and some other misc items')

    # here we add all the optional arguments
    # these will show up when -h or --help is called
    parser.add_argument('-o', type = str, help='The output path where the extracted data will be saved')

    # here we do the positional arguments like the url
    parser.add_argument('text', type=str, help='The url to be scraped and downloaded')

    # next we parse the arguments
    args = parser.parse_args()

    # finally we call the main function with all the args we just got
    main(args)
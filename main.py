import argparse

def main(args):
    '''Does all the downloading stuff with the passed in args'''

if __name__ == '__main__':
    '''This does all the handling of the arguments when run from the command line'''
    # first we declare a parser to parse the arguments
    # the description is the description that will appear near the top when -h or --help is called
    parser = argparse.ArgumentParser(description='Scraping Tool is a scraper with a cli coded in python3. It\'s main use is scraping manga, webtoons, and some other misc items')

    # here we add all the optional arguments
    # these will show up when -h or --help is called
    # parser.add_argument('--start_chapter', help='The starting chapter the scraper will start at')

    # here we do the positional arguments like the url
    parser.add_argument('text', type=str, help='The url to be scraped and downloaded')

    # next we parse the arguments
    args = parser.parse_args()

    # finally we call the main function with all the args we just got
    main(args)
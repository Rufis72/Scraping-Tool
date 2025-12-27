import argparse
from .main import format, download

if __name__ == '__main__':
    '''This does all the handling of the arguments when run from the command line'''
    # first we declare a parser to parse the arguments
    # the description is the description that will appear near the top when -h or --help is called
    parser = argparse.ArgumentParser(description='mangadl is a simple cli for scraping and formatting manga.')

    # creating the subparser so we can have multiple sub commands like main.py download and main.py format
    subparsers = parser.add_subparsers(dest='command', required=True)

    # creating the subcommands
    download_parser = subparsers.add_parser('download', help='Downloads a url from a supported website, or searches then downloads the chosen search result with -s')
    format_parser = subparsers.add_parser('format', help='Formats downloaded manga into a given file format')

    # ------------------------------------------------------------------------- DOWNLOAD -------------------------------------------------------------------------
    # create a mutually exclusive group 
    download_group = download_parser.add_mutually_exclusive_group(required=True)

    # add the --list-ids argument to the group
    download_group.add_argument('--list-ids', action='store_true', help='Lists all valid website IDs')

    # add the text argument to the group
    download_group.add_argument('text', type=str, nargs='?', help='The url to be downloaded')

    # add the search arguments to the group
    download_group.add_argument('--search', '-s', type=str, help='If we should search for the manga to be downloaded, and what query to use')
    download_parser.add_argument('--count', type=int, help='How many search results to take from each website when searching all websites. Default is 3', default=3)

    # all the normal download flags
    download_parser.add_argument('--output', '-o', type=str, help='The output path where the extracted data will be saved')
    download_parser.add_argument('--adult', '-a', type=bool, help='If search results should include adult content')
    download_parser.add_argument('--chapter', '-c', type=str, help='The specific chapter to be downloaded from a series. I.e, if you wanna download chapter four of one piece, you could pass -c 4. It can also be multiple chapters like: --chapter 0-4, or --chapter 0:4')
    download_parser.add_argument('--website', '-w', type=str, help='The ID of a website to be searched instead of all websites')
    download_parser.add_argument('--redownload', action='store_true', default=False, help='If chapters should be redownloaded, even if already downloaded. Defaults to false.')

    # ------------------------------------------------------------------------- FORMAT -------------------------------------------------------------------------


    format_parser.add_argument('--output', '-o', type=str, help='The path to where the formatted content will be outputed. Can be a directory (~/output/path), or a path to a file where it will infer the file type format the content as (~/output/file.pdf)')
    format_parser.add_argument('--input', '-i', type=str, help='The path to the content to be formatted. Only neccessary if the content being formatted wasn\'t downloaded with this command', required=True)
    format_parser.add_argument('--is-series', type=bool, help='If -i is a series, or only a single chapter/episode')
    format_parser.add_argument('--content-format', type=str, help='The way to format the content (manga/webtoon). Manga is every image on it\'s own page, webtoon is images are stacked on top of eachother, chapters are one 1 page each.')
    format_parser.add_argument('--chapters-per-file', type=int, help='The amount of chapters/episodes to put per file. Requires -o to be a directory', default=None)
    format_parser.add_argument('--chapter-naming-scheme', type=str, help='How to name files when formatting into multiple files using --chapters-per-file', default='[series_name] chapter [chapter_start]-[chapter_end]')
    format_parser.add_argument('--file-format', type=str, help='The file format to formata the content into. Only required if -o isn\'t a path to a file (~/output/file.pdf)')
    format_parser.add_argument('--series-name', type=str, help='The name of the series. Defaults to \'\', only used if using --chapters-per-file')
    format_parser.add_argument('--infer-series-name', type=bool, help='If --series-name should try to be inferred if not passed', default=True)
    format_parser.add_argument('--disable-warnings', help='If warnings such as defaulting to manga for formatting should be disabled', action='store_true')

    # next we parse the arguments
    args = parser.parse_args()

    # finally we call the correct function for the subcommand
    # format() for format, or download() for download
    if args.command == 'download':
        download(args)

    elif args.command == 'format':
        format(args)
from ebooklib import epub
import os
from mangadl import common
from mangadl.common import sort_strings_naturally, SharedChapterFormatterClass, SharedSeriesFormatterClass
import math
import shutil

class EPUBMangaChapter(SharedChapterFormatterClass):
    '''A class for saving a chapter as a PDF'''
    def __init__(self, content_path: str):
        ''':param content_path: The path to the directory with the images in it'''
        self.content_path = content_path

    def format(self, output_path: str):
        '''Formats a chapter's images as a PDF and saves it to the output path.
        :param output_path: The path to the file where the PDF will be saved. If the path to a directory is passed, it will create a output.pdf file'''
        # getting the list of all images
        image_paths = self.get_images()

        # ending the function and telling the user that formatting failed for this chapter if the passed content path was empty
        if len(image_paths) == 0:
            print(f'Could not find any images in directory {self.content_path}. Skipping...')
            return None

        # adding output.epub to the output_path if output_path is a directory
        if os.path.isdir(output_path):
            output_path = os.path.join(os.path.join(output_path, 'output.epub'))

        # creating an object for the chapter
        chapter_epub = epub.EpubBook()

        # setting metadata
        # title
        chapter_epub.set_title('.'.join(os.path.basename(output_path).split('.')[:-1]))
        # author
        chapter_epub.add_author('mangadl')

        # making a chapter for all the images we're about to add
        chapter = epub.EpubHtml(title='Chapter', file_name='chapter.xhtml', lang='en')

        # making a string to store the html content for all the images we're about to add
        chapter_content = '<html><body>'

        # adding the images to the book
        for i, image_path in enumerate(image_paths):
            # making a object for the image
            image_object = epub.EpubImage()

            # setting the image's data
            image_object.set_content(open(image_path, 'rb').read())

            # setting the filename
            image_object.file_name = os.path.basename(image_path)

            # adding the image to the book
            chapter_epub.add_item(image_object)

            # adding the image to the chapter's html content
            chapter_content += f'<img src="{image_object.get_name()}" style="width:100%";"/>'

        # closing the body and html tags for the chapter html content
        chapter_content += '</body></html>'

        # set the chapter content
        chapter.set_content(chapter_content)

        # add the chapter to the book
        chapter_epub.add_item(chapter)

        # defining the spine and main content
        # what does that mean? I don't know, but the docs said to do it, so we're doing it
        chapter_epub.spine = ['nav', chapter]

        # saving the book
        epub.write_epub(output_path, chapter_epub)


class EPUBMangaSeries(SharedSeriesFormatterClass):
    '''A class for saving a series as a PDF'''

    def format(self, output_path: str, chapters_per_pdf: int = None, pdf_chapter_naming_scheme: str = '[series_name] chapter [chapter_start]-[chapter_end]', series_name: str = ''):
        '''Formats a serie's images as a PDF and saves it to the output path
        :param chapters_per_pdf: How many chapters to put per PDF. It will raise an error if output_path is not a directory, as this will output multiple files.
        :param pdf_chapter_naming_scheme: How to format the file names. You can put [series_name], [chapter_start] and [chapter_end] to sub in as special values. [series_name] is the name of the series, [chapter_start] is the chapter that that pdf started at. If using chapters_per_pdf, it will be that, otherwise it will be 0. [chapter_end] is the same, but in this case the chapter it ended at
        :param output_path: The path to the file where the PDF will be saved. If the path to a directory is passed, it will create a output.pdf file'''
        # getting every chapter in the directory
        chapter_directories = self.get_chapters()

        # raising an error if there's no directorys in the passed directory
        if len(chapter_directories) == 0:
            raise Exception(f'{self.content_path} does not appear to have any directories in it. Are you sure it\'s a series directory?')
        
        # now we use a for loop for formatting into multiple files
        # even if it's only 1 file, we still use the for loop, we just then have them all formatted at once, and name the file differently
        # because we're using the loop even if we aren't seperating it into multiple files, then we first make a variable to store how many times we'll be looping for readability
        how_many_files_to_make = 0
        if chapters_per_pdf is None:
            how_many_files_to_make = 1
        else:
            # the ceil here is to make it so if it's 40 chapters, and 20 per file, that's 2 files, but if its 41 chapters, then instead of it being 2.05 files (which you can't really do) it's 3
            how_many_files_to_make = math.ceil(len(chapter_directories) / chapters_per_pdf)

        # now we do the actual loop
        for split_up_file_number in range(how_many_files_to_make):
            # getting all the chapter directories we'll be formatting this iteration of the for loop
            chapters_to_format_this_time = []
            
            # if we're not making more than 1 file, then we just get all chapters
            if how_many_files_to_make == 1:
                chapters_to_format_this_time = chapter_directories
            # otherwise we get the ones we're formatting this time
            else:
                chapters_to_format_this_time = chapter_directories[split_up_file_number * chapters_per_pdf, min(len(chapter_directories), (split_up_file_number + 1) * chapters_per_pdf)]

            # now we make an object for the epub file
            book = epub.EpubBook()

            # setting some book metadata
            book.add_author('mangadl')

            # we also make a variable to store all the chapter objects for later when we need to make the spine
            chapters = []

            # then we go through every chapter and make it, then add it to the book
            for chapter_num, chapter_directory in enumerate(chapters_to_format_this_time):
                # making a chapter item
                # first we make a variable for the chapter number
                chapter_number = chapter_num + (split_up_file_number * (0 if chapters_per_pdf is None else chapters_per_pdf)) + 1

                # then we actually make the chapter
                chapter = epub.EpubHtml(title=f'Chapter {chapter_number}', file_name=f'chapter{chapter_number}.xhtml', lang='en')

                # after that we make a variable to store the html for the chapter
                chapter_html_content = '<html><body>'

                # now we get the images in the directory
                image_paths = []
                for file_path in os.listdir(os.path.join(self.content_path, chapter_directory)):
                    if common.is_image_filename(file_path):
                        image_paths.append(os.path.join(self.content_path, chapter_directory, file_path))

                # sorting image paths, since for some reason os.listdir doesn't seme to return a sorted list
                image_paths = sorted(image_paths)

                # if there were no images in the chapter, we skip it and tell the user
                if len(image_paths) == 0:
                    print(f'No images were found in {chapter_directory}, skipping...')
                    continue

                # adding the images to the book
                for i, image_path in enumerate(image_paths):
                    # making a object for the image
                    image_object = epub.EpubImage()

                    # setting the image's data
                    image_object.set_content(open(image_path, 'rb').read())

                    # setting the filename
                    image_object.file_name = f'{chapter_num}-{os.path.basename(image_path)}'

                    # adding the image to the book
                    book.add_item(image_object)

                    # adding the image to the chapter's html content
                    chapter_html_content += f'<img src="{image_object.get_name()}" style="width:100%";"/>'

                # ending off the html and body tags for chapter's html
                chapter_html_content += '</body></html>'

                # setting the chapters content
                chapter.content = chapter_html_content

                # adding the chapter to the book
                book.add_item(chapter)

                # adding the chapter to our list of chapters
                chapters.append(chapter)

            # adding the spine
            book.spine = ['nav'] + chapters

            # saving the book
            # first we get the new output path
            if os.path.isdir(output_path):
                new_output_path = os.path.join(
                    output_path, 
                    pdf_chapter_naming_scheme.replace('[series_name]', series_name).replace('[chapter_start]', str(i * chapters_per_pdf)).replace('[chapter_end]', str(min(len(chapter_directories) - 1, (i + 1) * chapters_per_pdf))) + '.epub'
                )
            else:
                new_output_path = output_path

            # now we save it
            epub.write_epub(new_output_path, book)
from PIL import Image
from PyPDF2 import PdfMerger, PdfWriter
import os
from mangadl import common
from mangadl.common import sort_strings_naturally
import math
import shutil

class PDFMangaChapter:
    '''A class for saving a chapter as a PDF'''
    def __init__(self, content_path: str):
        ''':param content_path: The path to the directory with the images in it'''
        self.content_path = content_path

    def format(self, output_path: str):
        '''Formats a chapter's images as a PDF and saves it to the output path.
        :param output_path: The path to the file where the PDF will be saved. If the path to a directory is passed, it will create a output.pdf file'''
        # getting the list of all images
        # what we do is we go through every file in the directory and check if it's a img file
        # if it is, we add it to the list of filenames
        image_filenames = []
        for filename in sorted(os.listdir(self.content_path)):
            if common.is_image_filename(filename):
                image_filenames.append(os.path.join(self.content_path, filename))

        # ending the function and telling the user that formatting failed for this chapter if the passed content path was empty
        # we just make an empty pdf to satisfy the Series pdf merging
        if len(image_filenames) == 0:
            print(f'Could not find any images in directory {self.content_path}. Skipping...')

            # making the empty pdf
            writer = PdfWriter()
            # saving it
            with open(output_path, 'wb') as f:
                writer.write(f)

            return None

        # adding output.pdf to the output_path if output_path is a directory
        if os.path.isdir(output_path):
            output_path = os.path.join(os.path.join(output_path, 'output.pdf'))

        # loading all the images
        images = [Image.open(image_filename) for image_filename in image_filenames]

        # saving the pdf
        images[0].save(
            output_path, 'PDF', resolution=100.0, save_all=True, append_images=images[1:]
        )

class PDFMangaSeries:
    '''A class for saving a series as a PDF'''
    def __init__(self, content_path: str):
        ''':param content_path: The path to the directory with the chapter directorys with images in it'''
        self.content_path = content_path

    def format(self, output_path: str, chapters_per_pdf: int = None, pdf_chapter_naming_scheme: str = '[series_name] chapter [chapter_start]-[chapter_end]', series_name: str = ''):
        '''Formats a serie's images as a PDF and saves it to the output path
        :param chapters_per_pdf: How many chapters to put per PDF. It will raise an error if output_path is not a directory, as this will output multiple files.
        :param pdf_chapter_naming_scheme: How to format the file names. You can put [series_name], [chapter_start] and [chapter_end] to sub in as special values. [series_name] is the name of the series, [chapter_start] is the chapter that that pdf started at. If using chapters_per_pdf, it will be that, otherwise it will be 0. [chapter_end] is the same, but in this case the chapter it ended at
        :param output_path: The path to the file where the PDF will be saved. If the path to a directory is passed, it will create a output.pdf file'''
        # getting every chapter in the directory
        chapter_directory_names = sorted([d for d in os.listdir(self.content_path) if os.path.isdir(os.path.join(self.content_path, d))])

        # raising an error if there's no directorys in the passed directory
        if len(chapter_directory_names) == 0:
            raise Exception(f'{self.content_path} does not appear to have any directories in it. Are you sure it\'s a series directory?')

        # formatting a pdf for every chapter temporarily
        # first we make a directory to save these in
        # if the output_path is a directory, we just add temp-[32 random characters] to the path, otherwise we add temp-[32 random characters] to the output_path's parent directory
        if os.path.isdir(output_path):
            temp_path = os.path.join(output_path, f'.temp-{common.generate_random_string(32)}')
        else:
            temp_path = os.path.join(os.path.dirname(output_path), f'.temp-{common.generate_random_string(32)}')
        os.mkdir(temp_path)

        chapter_pdf_paths = []

        # we sort the chapters here, since because of how naming works (they're taken from the website directly), there isn't typically leading 0s
        for i, chapter_directory_name in enumerate(sort_strings_naturally(chapter_directory_names)):
            # giving an update to the user that we've started making pdfs for the chapters
            print(f'Started formatting chapter {i} as a PDF')

            # then we format everything and save it there
            # first we make a PDFMangaChapter object for the chapter
            chapter_object = PDFMangaChapter(os.path.join(self.content_path, chapter_directory_name))

            # then we format it
            chapter_object.format(os.path.join(temp_path, f'chapter {i:02d}.pdf'))

            # we also save the name for future use
            chapter_pdf_paths.append(os.path.join(temp_path, f'chapter {i:02d}.pdf'))

        # now we merge them
        # to do that, we need to know how many chapters to put per pdf, so we get that here
        # the reason we can't just use chapters_per_pdf is that the user might just want one big pdf
        if chapters_per_pdf == None:
            chapters_per_pdf = len(chapter_directory_names)

        # now we merge them
        for i in range(math.ceil(len(chapter_directory_names) / chapters_per_pdf)):
            # telling the user we're merging the PDFs
            print(f'Started merging the individual chapter PDFs ({i + 1}/{math.ceil(len(chapter_directory_names) / chapters_per_pdf)})')

            # first we get the chapters we're merging
            pdfs_to_merge_paths = chapter_pdf_paths[i * chapters_per_pdf:(min(len(chapter_directory_names), (i + 1) * chapters_per_pdf))]

            # then we merge them
            merger = PdfMerger()

            for pdf in pdfs_to_merge_paths:
                merger.append(pdf)

            # saving the file
            # if the output path is a directory, we add the formatted pdf chapter name to the output path, otherwise, we just use the passed output_path
            if os.path.isdir(output_path):
                new_output_path = os.path.join(
                    output_path, 
                    pdf_chapter_naming_scheme.replace('[series_name]', series_name).replace('[chapter_start]', str(i * chapters_per_pdf)).replace('[chapter_end]', str(min(len(chapter_directory_names) - 1, (i + 1) * chapters_per_pdf))) + '.pdf'
                )
            else:
                new_output_path = output_path

            merger.write(new_output_path)
            merger.close()

        # deleting the temp directory
        shutil.rmtree(temp_path)
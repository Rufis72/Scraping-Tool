from PIL import Image
from PyPDF2 import PdfMerger
import os
import common
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
        images = []
        for filename in sorted(os.listdir(self.content_path)):
            if ['.png', '.jpeg', '.jpg', '.gif'].__contains__(os.path.splitext(filename)[-1].lower()):
                images.append(Image.open(os.path.join(self.content_path, filename)))

        # adding output.pdf to the output_path if output_path is a directory
        if os.path.isdir(output_path):
            output_path = os.path.join(os.path.join(output_path, 'output.pdf'))

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

        # formatting a pdf for every chapter temporarily
        # first we make a directory to save these in
        # if the output_path is a directory, we just add temp-[32 random characters] to the path, otherwise we add temp-[32 random characters] to the output_path's parent directory
        if os.path.isdir(output_path):
            temp_path = os.path.join(output_path, f'temp-{common.generate_random_string(32)}')
        else:
            temp_path = os.path.join(os.path.dirname(output_path), f'temp-{common.generate_random_string(32)}')
        os.mkdir(temp_path)

        chapter_pdf_paths = []

        for i, chapter_directory_name in enumerate(chapter_directory_names):
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
            # first we get the chapters we're merging
            pdfs_to_merge_paths = sorted(chapter_pdf_paths)[i * chapters_per_pdf:min(len(chapter_directory_names) - 1, (i + 1) * chapters_per_pdf)]

            print(chapter_pdf_paths)

            # then we merge them
            merger = PdfMerger()

            for pdf in pdfs_to_merge_paths:
                print(pdf)
                merger.append(pdf)

            # saving the file
            # if the output path is a directory, we add the formatted pdf chapter name to the output path, otherwise, we just use the passed output_path
            if os.path.isdir(output_path):
                output_path = os.path.join(
                    output_path, 
                    pdf_chapter_naming_scheme.replace('[series_name]', series_name).replace('[chapter_start]', str(i * chapters_per_pdf)).replace('[chapter_end]', str(min(len(chapter_directory_names) - 1, (i + 1) * chapters_per_pdf))) + '.pdf'
                )
            
            merger.write(output_path)
            merger.close()

        # deleting the temp directory
        shutil.rmtree(temp_path)


a = PDFMangaSeries('/home/Rufis/scraping-tool-dev/Scraping-Tool-1/dr-stone_108')
a.format('/home/Rufis/scraping-tool-dev/Scraping-Tool-1')
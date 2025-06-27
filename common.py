import os.path

class Image(bytes):
    '''This is a class to represent a downloaded image
    This class literally is just a bytes object with an extra save function

    Example Code:
    form common import Image

    # here we make an object for the Image
    img = Image(b'put/bytes/of/your/image/here')

    # then we save it using it's save function
    img.save('/put/the/path/to/where/you/wanna/save/it/here.filetype'
    '''

    def __new__(cls, image: bytes):
        # Create a new instance of the bytes class
        return super().__new__(cls, image)

    def save(self, path: str):
        '''Saves the image to a specified path

        Example Code:
        from common import Image

        # here we define the Image object
        img = Image(b'put/bytes/here')

        # then we save it
        img.save('/path/to/where/you/wanna/save/it.filetype')

        :param path: The path to where the image will be saved
        '''
        # first we open the file
        # python will make the file for us if it doesn't exist
        with open(path, 'wb') as f:
            # now we write the bytes of the image
            f.write(self)

class ImageDownloads(list[Image]):
    '''The image downloads for a chapter
    The class is just a list[bytes] with a save function

    Example Code:
    from common import ImageDownloads

    # here we declare the ImageDownloads object with the list of bytes
    img_downloads = ImageDownloads([b'put/your/bytes/here', b'put/some/more/bytes/here'...])

    # here you can save the images to a given path
    # it will save all the images to /path/to/where/saving/it/0001.png, /path/to/where/saving/it/0002.png, etc
    img_downloads.save('/path/to/where/you/wanna/save/it')
    '''
    def __init__(self, images: list[Image]):
        super().__init__(images)

    def save(self, path):
        '''Saves the images to a given path
        :param path: The path where the images will be saved

        Example Code:
        images = [b'/x89PNG/r/n/x1a/n...', b'/x89PNG/r/n/x1a/n...']  # Replace with actual image bytes
        image_downloads = ImageDownloads(images)
        image_downloads.save("/path/to/save")
        '''
        # the for loop goes through every image object
        for i, image_object in enumerate(self):
            # then this line of code just saves it
            image_object.save(f"{path}/{i:04d}.png")

class SeriesImageDownloads(list[ImageDownloads]):
    ''''''
    def __init__(self, list_of_ImageDownloads_objects: list[ImageDownloads]):
        super().__init__(list_of_ImageDownloads_objects)

    def save(self, path: str):
        '''Saves all the images of a series to a given path
        The images will be seperated by chapter like this:
        chapter_1: /path/1/0001.png, /path/001/0002.png, etc
        chapter_2: /path/2/0001.png, /path/002/0002.png, etc
        etc
        This function will assume the first object in the list is path/1, the second is path/2, etc

        Example Code:
        from common import ImageDownloads, SeriesImageDownloads

        # here you'd get a list of ImageDownloads object somehow
        # this could be from downloading a bunch of chapters, or however
        series_img_downloads = [ImageDownloads(b'bytes/here'...)...]

        # now you could save them all individually, or you can use SeriesImageDownloads
        # SeriesImageDownloads basically acts as a way to bundle all those together, and save them easily instead of having to write code to save each one individually every time
        series_img_downloads_object = SeriesImageDownloads(series_img_downloads)
        series_img_download_object.save('/path/where/you/wanna/save/it')

        :param path: The path where the images will be saved'''
        # going through every ImageDownloads object in self and calling save on it
        for i, img_downloads_object in enumerate(self):
            img_downloads_object.save(os.path.join(path, f'{i:03d}'))

class SearchResult:
    '''This is the class for search results from manga websites
    IMPORTANT NOTE: website should be the name of the scraper file for that website

    Example Code:
    from mangaread import search

    '''
    def __init__(self, name: str, url: str, website: str):
        self.name = name
        self.url = url
        self.website = website

def generate_text_with_link(uri, label=None):
    if label is None:
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)
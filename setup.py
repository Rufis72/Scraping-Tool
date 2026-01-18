from setuptools import setup, find_packages

setup(
    name='mangadl',
    version='1.1.0',
    description='A simple cli for scraping and formatting manga.',
    author='Rufis72',
    license='MIT',
    url='https://github.com/Rufis72/mangadl',
    install_requires=[
        'requests>=2.32.4',
        'beautifulsoup4>=4.13.4',
        'pillow>=12.0.0',
        'PyPDF2>=3.0.1',
        'reportlab>=4.4.4',
        'ebooklib>=0.20'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mangadl = mangadl.main:run',
        ],
    },
)
<h1 align="center">Scraping Tool</h1>
<p align="center">
<a href="https://github.com/Rufis72/Scraping-Tool/blob/master/LICENSE"><img src="https://img.shields.io/github/license/Rufis72/Scraping-Tool.svg?style=for-the-badge" alt="License"></a>
</p>

## Supported Sources
- natomanga (search currently broken due to Cloudflare)
- webtoons.com
- bato.to
- mangabuddy.com
- mangaread.org
- mangatown.com
- 1manga.co
- tapas.io
## Installation
### Prerequisites
Before installing, make sure you have a semi-recent version of [pip](https://pypi.org/project/pip/) (or your Python package manager of choice) and [Python](https://www.python.org/downloads/) installed.
### Installation
```shell
git clone https://github.com/Rufis72/Scraping-Tool
cd Scraping-Tool
pip3 install -r requirements.txt
```
### Setup
Once you finish installation, it's recommended to add main.py to PATH so you can use it from anywhere. You may also want to rename main.py to something like mangadl to make it easier to remember
On Unix systems, make sure to make main.py executable with `chmod +x main.py`

## Usage
### Examples
Download a manga via it's url
```shell
python3 main.py download 'https://bato.to/title/83510-one-piece-official'
```
Download a manga via searching
```shell
python3 main.py download -s 'One Piece'
```
Download a manga via searching on a specific website
```shell
python3 main.py download -s 'One Piece' -w bato
```
List all possible websites to search on specifically
```shell
python3 main.py download --list-ids
```
Download a specific chapter of a manga
```shell
python3 main.py download 'https://bato.to/title/83510-one-piece-official' -c 1146
```
Download multiple chapters
```shell
python3 main.py download -s 'One Piece' -c 1100:1146
```
Format downloaded manga as a PDF (formatting it as one image per page)
```shell
python3 main.py format -i ./One\ Piece -o ./output.pdf
```
Format downloaded webtoons as a PDF (formatting it as one chapter per page, so every new image is placed below the old one)
```shell
python3 main.py format -i ./Hero\ Killer -o ./output.pdf --content-format webtoon
```
Format a series as a PDF, but split it up into multiple files by chapter count
```shell
python3 main.py format -i ./One\ Piece -o ./output.pdf --chapters-per-file 20
```


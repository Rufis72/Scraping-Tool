<h1 align="center">mangadl</h1>
<p align="center">
<a href="https://github.com/Rufis72/mangadl/blob/master/LICENSE"><img src="https://img.shields.io/github/license/Rufis72/mangadl.svg?style=for-the-badge" alt="License"></a>
</p>

## Supported Sources
- [natomanga](https://natomanga.com)/[mangakalot](https://mangakakalove.com) (search currently broken due to Cloudflare)
- [webtoons.com](https://webtoons.com)
- [bato.to](https://bato.to) (and [proxies](https://batomirrors.pages.dev))
- [mangabuddy.com](https://mangabuddy.com)
- [mangaread.org](https://mangaread.org)
- [mangatown.com](https://mangatown.com)
- [1manga.co](https://1manga.co)
- [tapas.io](https://tapas.io)
- [comix.to](https://comix.to)
- [mangadex.org](https://mangadex.org) (only chapters hosted on mangadex.org)
## Installation
### Prerequisites
Before installing, make sure you have a semi-recent version of [pip](https://pypi.org/project/pip/) (or your Python package manager of choice) and [Python](https://www.python.org/downloads/) installed.
### Installation
```shell
git clone https://github.com/Rufis72/mangadl
cd mangadl
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
mkdir output
python3 main.py format -i ./One\ Piece -o ./output --chapters-per-file 20 --file-format pdf
```


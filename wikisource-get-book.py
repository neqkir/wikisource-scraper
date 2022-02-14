import os
import re
import sys
import time
import urllib
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup
import requests
import tqdm

BOOK_TO_SCRAP = "Micromégas"
WITH_SUBTITLES = True

def get_content_page(url):

    res = urllib.request.urlopen(url)
    wiki = BeautifulSoup(res, "lxml")

    elems = wiki.select('p')

    text = ""
    
    for elem in elems:
        text += re.sub(r"\n", " ", elem.getText())
        text += "\n"

    text = re.sub(r"(\[\d+\])+", "", text)

    return text

def get_book_urls(lang, url_title):
    '''
    For a given wikisource book, e.g.,
    https://en.wikisource.org/wiki/Merchant_of_Venice_(1923)_Yale
    fetches all urls for book parts (chapters, acts etc.)
    '''
    pages = []

    url = "https://" + lang + ".wikisource.org/wiki/" + url_title
    req = urllib.request.urlopen(url)
    wiki = BeautifulSoup(req, "lxml")

    for link in wiki.find(id="bodyContent").findAll('a'):
         
        if link['href'].find("/wiki/"+url_title) == -1:
            continue
        else:
            print(str(link.get('href')))
            pages.append("https://fr.wikisource.org/" + str(link.get('href')))

    #print(pages)
        
    return pages
    
    
def get_book(lang, url_title):
    
    content = ""
    url = "https://" + lang + ".wikisource.org/wiki/" + url_title
    req = urllib.request.urlopen(url)
    wiki = BeautifulSoup(req, "lxml")

    # Get book title
    
    title = wiki.title.string
    print(title)

    # Get all urls (for parts, chapters, acts etc.)

    urls = get_book_urls(lang, url_title)
    pbar = tqdm.tqdm(urls)

    for url in pbar:
        content += get_content_page(url) + " "
        pbar.set_description("Processing %s" % url.split('/')[-2])
        
    return title, content
    
def save_to_file(text, title):
    f = '":.*<>|/\\?'
    for char in f:
        if char in title:
            title = title.replace(char, " ")
    if not os.path.exists('Wikitexts'):
        os.makedirs('Wikitexts')
    #print(title)
    with open(os.path.join('Wikitexts', title + ".txt"), "w", encoding="utf8") as file:
        file.write(text)
    return


if __name__ == "__main__":

    url_title = BOOK_TO_SCRAP

    url_title = urllib.parse.quote(url_title)

    titre, livre = get_book("fr", url_title)

    save_to_file(livre, titre)

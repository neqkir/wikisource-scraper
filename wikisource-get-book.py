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

# Other examples
#BOOK_TO_SCRAP = "Merchant_of_Venice_(1923)_Yale"
#BOOK_TO_SCRAP = "Poésies_(Mallarmé,_1914,_8e_éd.)"

WITH_SUBTITLES = True


##def remove_dups(file):
##    uniques = set()
##    with open(file, "r", encoding="utf8") as f:
##        for link in tqdm.tqdm(f.readlines()):
##            url = urllib.parse.quote(link)
##            page, _ = get_source(url)
##            uniques.add('/'.join(page.split('/')[4:]).strip())
##    with open(file, 'w+') as f:
##        for item in uniques:
##            print(item)
##            f.write("https://fr.wikisource.org/wiki/%s\n" % item)

def get_content_page(url):

    res = urllib.request.urlopen(url)
    wiki = BeautifulSoup(res, "lxml")

    title = wiki.title.string
    
    text = ""
    elems = wiki.select('p')
    
    for elem in elems:
        text += re.sub(r"\n", " ", elem.getText())
        text += "\n"

    text = re.sub(r"(\[\d+\])+", "", text)

    return title, text

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
        page_title, page_content = get_content_page(url) 
        if WITH_SUBTITLES:
            content += "\n" + page_title + "\n"
        content += page_content + " "
        pbar.set_description("Processing %s" % url.split('/')[-2])
        
    return title, content
    
def save_to_file(text, title):
    f = '":.*<>|/\\?'
    for char in f:
        if char in title:
            title = title.replace(char, " ")
    if not os.path.exists('Wikitexts'):
        os.makedirs('Wikitexts')
    with open(os.path.join('Wikitexts', title + ".txt"), "w", encoding="utf8") as file:
        file.write(text)
    return


if __name__ == "__main__":

    url_title = urllib.parse.quote(BOOK_TO_SCRAP)
    titre, livre = get_book("fr", url_title)
    save_to_file(livre, titre)


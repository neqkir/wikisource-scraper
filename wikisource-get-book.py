import os
import re
import sys
import time
import urllib
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup
import requests
import tqdm

LANGUAGE = "en"

BOOK_TO_SCRAP = "Micromégas"
# Other examples
BOOK_TO_SCRAP = "Merchant_of_Venice_(1923)_Yale"
#BOOK_TO_SCRAP = "Poésies_(Mallarmé,_1914,_8e_éd.)"

WITH_SUBTITLES = True

# Exlude specific pages (page name starting with)
EXCLUDE = ["Appendix", "Index", "Bibliography", "Notes" ]

NO_FOOT_NOTES = True


def get_content_page(url):

    print(url)

    res = urllib.request.urlopen(url)
    wiki = BeautifulSoup(res, "lxml")

    title = wiki.title.string

    text = ""
    elems = wiki.select('p')

    
    for elem in elems:

        if NO_FOOT_NOTES and (elem.text.startswith("Footnotes")):
            break

        text += re.sub(r"\n", " ", elem.text)
        text += "\n"

    text = re.sub(r"(\[\d+\])+", "", text)

    return title, text



def get_book_urls(url_title):
    '''
    For a given wikisource book, e.g.,
    https://en.wikisource.org/wiki/Merchant_of_Venice_(1923)_Yale
    fetches all urls for book parts (chapters, acts etc.)
    '''
    
    pages = []

    url = "https://" + LANGUAGE + ".wikisource.org/wiki/" + url_title
    req = urllib.request.urlopen(url)
    wiki = BeautifulSoup(req, "lxml")

    for link in wiki.find(id="bodyContent").findAll('a'):

        # exclude everything non wikisource text page
        
        excl1 = link['href'].find("/wiki/"+url_title) 
        excl2 = link['href'].find("/wiki/"+BOOK_TO_SCRAP)

        if excl1 == -1 and excl2 == -1:
            continue

        # exclude pages corresponding to elements in EXCLUDE
        # e.g., appendix, notes, bibliography etc.
        # e.g, if EXCLUDE = ["appendix", "notes"] for https://en.wikisource.org/wiki/Merchant_of_Venice_(1923)_Yale
        # it will exclude pages whose name (after /wiki/Merchant_of_Venice_(1923)_Yale/) starts with appendix or notes
        

        exclude_list = ["/wiki/" + url_title.lower() + "/" + i.lower() for i in EXCLUDE]+\
                       ["/wiki/" + BOOK_TO_SCRAP.lower() + "/" + i.lower() for i in EXCLUDE]

        if any(elem in link['href'].lower() for elem in exclude_list):
            continue

        #print(str(link.get('href')))         
        pages.append("https://" + LANGUAGE + ".wikisource.org/" + str(link['href']))

    #print(pages)
        
    return pages
    

    
def get_book(url_title):
    
    content = ""
    url = "https://" + LANGUAGE + ".wikisource.org/wiki/" + url_title
    req = urllib.request.urlopen(url)
    wiki = BeautifulSoup(req, "lxml")

    # Get book title
    
    title = wiki.title.string
    print(title)

    # Get all urls (for parts, chapters, acts etc.)

    urls = get_book_urls(url_title)
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
    titre, livre = get_book(url_title)
    save_to_file(livre, titre)


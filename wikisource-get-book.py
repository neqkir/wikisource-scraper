import os
import re
import sys
import time
import urllib
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup
import requests
import tqdm

############# MANDATORY INPUTS

# Wikisource book to scrap
BOOK_TO_SCRAP = "Micromégas"
# Other examples
BOOK_TO_SCRAP = "Merchant_of_Venice_(1923)_Yale"
BOOK_TO_SCRAP = "Poésies_(Mallarmé,_1914,_8e_éd.)"

# And its language
LANGUAGE = "fr"
#LANGUAGE = "en"

###################################################

# Exlude specific pages (page name starting with)
EXCLUDE = ["Appendix", "Index", "Bibliography", "Notes" ]

# With parts titles or not (acts, chapters, etc.)
WITH_SUBTITLES = True

# Remove foot notes
NO_FOOT_NOTES = True

###################################################

def get_content_page(url):

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

    url_title = url_title.replace("%28","(").replace("%29",")").replace("%2C",",")

    # screen over all weblinks
        
    for e in wiki.find(id="bodyContent").findAll('a'):

        # keep if has a class 'href'

        if e.has_attr('href') == 0 :
             continue

        # keep wiki pages
            
        if e['href'].find("/wiki/"+url_title) == -1 : 
            continue

        # exclude pages corresponding to elements in EXCLUDE
        # e.g., appendix, notes, bibliography etc.
        # e.g, if EXCLUDE = ["appendix", "notes"] for https://en.wikisource.org/wiki/Merchant_of_Venice_(1923)_Yale
        # it will exclude pages whose name (after /wiki/Merchant_of_Venice_(1923)_Yale/) starts with appendix or notes
        
        exclude_list = ["/wiki/" + url_title.lower() + "/" + i.lower() for i in EXCLUDE]

        if any(elem in e['href'].lower() for elem in exclude_list):
            continue

        pages.append("https://" + LANGUAGE + ".wikisource.org/" + str(e['href']))
        
    return pages
    

def clean_title(title):

    # cut after Wikisource 
    sub_str = "Wikisource"
    if(title.find(sub_str) > -1) :
        title = title[:title.index(sub_str)-2]

    # remove book title
    if(title.find(BOOK_TO_SCRAP) > -1) :
        title = title[title.index(BOOK_TO_SCRAP)+len(BOOK_TO_SCRAP):]
    
    return title
    

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
            content += "\n" + clean_title (page_title) + "\n"

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
    titre, livre = get_book(urllib.parse.quote(BOOK_TO_SCRAP))
    save_to_file(livre, titre)


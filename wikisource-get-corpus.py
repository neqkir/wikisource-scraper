### Wikisource scraper by neqkir
# get all books in a corpus

##### corpus.txt might look like
# Micromégas;;fr
# Merchant_of_Venice_(1923)_Yale;;en
# Poésies_(Mallarmé,_1914,_8e_éd.);;fr

# etc..

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
BOOK_TO_SCRAP = "Micromégas"
BOOK_TO_SCRAP = "Divagations_(1897)"

# And its language
LANGUAGE = "fr"
#LANGUAGE = "en"

###################################################

# Exlude specific pages (page name starting with)
EXCLUDE = ["Appendix", "Index", "Bibliography", "Bibliographie", "Notes", "Texte_entier" ]
# With parts titles or not (acts, chapters, etc.)
WITH_SUBTITLES = True
# Remove foot notes
NO_FOOT_NOTES = True
# Save all to a single file
SINGLE_FILE = True
TITLE_ALL = "mallarme"

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



def get_book_urls(url_title, language):
    '''
    For a given wikisource book, e.g.,
    https://en.wikisource.org/wiki/Merchant_of_Venice_(1923)_Yale
    fetches all urls for book parts (chapters, acts etc.)
    '''
    
    pages = []

    url = "https://" + language + ".wikisource.org/wiki/" + url_title
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
    

def clean_sub_title(subtitle, title):

    # cut after Wikisource 
    sub_str = "Wikisource"
    if(subtitle.find(sub_str) > -1) :
        subtitle = subtitle[:subtitle.index(sub_str)-2]

    # remove book title
    sub_str = title.replace("_"," ")
    if(subtitle.find(sub_str) > -1) :
        subtitle = subtitle[subtitle.index(sub_str)+len(sub_str):]

    subtitle = re.sub('[/\-*#]', '', subtitle)

    subtitle = subtitle.strip()
    print(subtitle)
    
    return subtitle


def clean_title(title):

    # cut after Wikisource 
    sub_str = "Wikisource"
    if(title.find(sub_str) > -1) :
        title = title[:title.index(sub_str)-2]

    title = re.sub('[/\-*#]', '', title)

    title = title.strip()
    
    return title


def clean_content(content, page_title):
    '''
    Unfortunately you'll have to work a little bit !
    Write in this function specific code to clean your specific text.
    '''
    rem_substr = "Pour les autres éditions de ce texte, voir " + page_title + " (Mallarmé)."

    if(content.find(rem_substr) > -1) :
        content = content[content.index(rem_substr)+len(rem_substr):]

    rem_substr = "Pour les autres éditions de ce texte, voir " + page_title + "."

    if(content.find(rem_substr) > -1) :
        content = content[content.index(rem_substr)+len(rem_substr):]

    ## Add stuff to remove non-text

    return content


def get_book(url_title, language):

    content = ""
    url = "https://" + language + ".wikisource.org/wiki/" + url_title
    req = urllib.request.urlopen(url)
    wiki = BeautifulSoup(req, "lxml")

    # Get book title
    
    title = clean_title(wiki.title.string)
    print("loading " + title + " ...")

    # Get all urls (for parts, chapters, acts etc.)

    urls = get_book_urls(url_title, language)
    pbar = tqdm.tqdm(urls)

    for url in pbar:
            
        page_title, page_content = get_content_page(url)

        page_title = clean_sub_title(page_title, title)

        if WITH_SUBTITLES:
            content += "\n" + page_title + "\n"
            
        page_content = clean_content(page_content, page_title)     

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
    
    # read list of books from the corpus
    
    try:
        f = open("corpus.txt", "r",encoding='utf-8', errors='ignore')
        lines = f.readlines()
        f.close()
        
    except (OSError, IOError) as e:
        print("no corpus provided, we'll just load one ...")
        lines = [BOOK_TO_SCRAP+";;"+LANGUAGE]

    books = ""
    for line in lines:
        book_to_scrap, language = line.strip().split(";;") 
        title, book = get_book(urllib.parse.quote(book_to_scrap), language)
        
        if SINGLE_FILE:
            books += book + "\n"
        else: 
            save_to_file(book, title)

    if SINGLE_FILE:
            save_to_file(books, TITLE_ALL)

        



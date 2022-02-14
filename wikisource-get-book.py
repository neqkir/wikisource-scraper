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


def get_source(page_url):
    soup = BeautifulSoup(urllib.request.urlopen(page_url), "lxml")
    title = soup.find(id="firstHeading").text
    tmp = soup.find("script").text.split("proofreadpage_source_href")

    if (len(tmp) == 1):
        return page_url, title

    else:
        page_url = "https://fr.wikisource.org" + tmp[1].split()[1].split('"')[1]
        page_url = page_url[:-1]
        return page_url, title

def remove_dups(file):
    uniques = set()
    with open(file, "r", encoding="utf8") as f:
        for link in tqdm.tqdm(f.readlines()):
            url = urllib.parse.quote(link)
            page, _ = get_source(url)
            uniques.add('/'.join(page.split('/')[4:]).strip())
    with open(file, 'w+') as f:
        for item in uniques:
            print(item)
            f.write("https://fr.wikisource.org/wiki/%s\n" % item)

def get_pages_url(source_url):
    pages = []
    try:
        line = urllib.request.urlopen(source_url)
        soup = BeautifulSoup(line, "lxml")
    except URLError:
        pages.append("Non scrappable")
        return pages
    for a in soup.findAll('a', {'class':['prp-pagequality-3 quality3', 'prp-pagequality-4 quality4']}):
        pages.append("https://fr.wikisource.org/" + a['href'])
        print(pages)
    if not pages:
        return [source_url]
    return pages

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
    # You can comment out this first line if the URL list is clean already (no dups).
    #remove_dups("/content/sample_data/urls.txt")
    #f = open("/content/sample_data/urls.txt", "r")
    #lines = f.readlines()
    #f.close()
    url_title = "Merchant_of_Venice_(1923)_Yale"
    url_title = "Poésies_(Mallarmé,_1914,_8e_éd.)"

    url_title = BOOK_TO_SCRAP

    url_title = urllib.parse.quote(url_title)

    #url = "https://fr.wikisource.org/wiki/Po%C3%A9sies_(Mallarm%C3%A9,_1914,_8e_%C3%A9d.)"
    #url = "https://fr.wikisource.org/wiki/Microm%C3%A9gas"

    titre, livre = get_book("fr", url_title)

    save_to_file(livre, titre)

    #for line in lines:
        #urllib.request.urlopen(urllib.parse.quote(line))
        #line = urllib.parse.quote(line)
        #livre, titre = get_content_pages(get_pages_url(line))
        #save_to_file(livre, titre)

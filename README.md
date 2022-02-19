# wikisource-scraper
complete wikisource scraper for natural language processing

`wikisource-get-book.py`

Writes to a text file the whole text for given url book in wikisource.
It can remove specific pages : notes, appendix, bibliography.
It works with a language of choice ; e.g., "en" for English, "fr" for French.

`wikisource-get-corpus.py`

Writes to a *single* text file the whole text for given books in corpus. Use this to feed a lot of data from the same author, genre, literary movement to your neural networks.

An example of corpus is given in `corpus.txt`. It can list pages with text and pages referring to multiple pages with text. 



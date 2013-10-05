Somerville Tree Audit Scraper
=============================

Somerville, MA, USA did a tree audit.  The results are posted on a website with public 
guest login so anyone can see the results.  The information wasn't available in a 
machine-readable format, so this software scrapes the website and creates a CSV file 
with all the information about each tree.

Installation
------------

Make sure you have Python2.7.  The install the requirements:

```
pip install mechanize
pip install BeautifulSoup
```

Running
-------

This can take a while, because there are a LOT of trees to query!  So this creates a 
`cache` directory so you can stop it and start it again.

```
python scrape.py
```

This will generate a `somerville-tree-details.csv` file in this folder with the results.

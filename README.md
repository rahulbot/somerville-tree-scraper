Somerville Tree Audit Scraper
=============================

Somerville, MA, USA did a tree audit.  The results are posted on a website with public 
guest login so anyone can see the results.  The information wasn't available in a 
machine-readable format, so this software scrapes the website and creates a CSV file 
with all the information about each tree.

Installation
------------

Make sure you have Python2.7.  Then install these requirements:

```
pip install mechanize
pip install BeautifulSoup
```

Running
-------

This can take a while, because there are a LOT of trees to query!  This creates a 
`cache` directory so you can stop it and start it again without taxing their servers too much.

```
python scrape.py
```

This will generate a `somerville-tree-details.csv` file in this folder with the results.

History
-------

In 2011 @Bostonography write a great "blog post":http://bostonography.com/2011/autumn-streets/ 
about data and kindly shared the results of their scraping with me.  I used this in a class I was
leading, and someone was interested so I wrote this scraper to:
 * get the park AND street listings
 * get all the metadata about each tree

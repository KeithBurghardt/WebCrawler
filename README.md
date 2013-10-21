WebCrawler
==========

World Of Knowledge Web Crawler Using Scrapy. 

This parses and stores paper metadata, like title, author, and  who referenced or cited the paper.

This code needs Python 2.7.x and scrapy 0.19

First type: scrapy startproject WebOfKnowledge

Edit items.py using attached code

go to the spiders/ sub-directory

Add "WebOfKnowledge_spider.py" code


To run type: scrapy crawl WebOfKnowledge -o CitationNetwork.json -t json -a start_url="http://start_url"


This creates a spider that stays in the apps.Webofknowledge.com domain and crawls through papers looking for
a paper's title, author and who cited/referenced it, and stores this data into CitationNetwork.json.

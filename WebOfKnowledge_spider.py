#=====================================Web Of Knowledge Spider ========================================

import urlparse
from scrapy.conf import settings
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider,Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from WebOfKnowledge.items import WebOfKnowledgeItem
from scrapy.utils.response import open_in_browser

# To run type: scrapy crawl WebOfKnowledge -o CitationNetworkAdes,IZ.json -t json -a start_url="http://start_url"


class WebOfKnowledgeSpider(CrawlSpider):
    settings.overrides['DEPTH_LIMIT']=5#was 10 for Ades, Iz* which was prematurely stopped after ~60 hours
    #=============================Breadth First Search Overrides===========================================
    settings.overrides['DEPTH_PRIORITY'] = 1
    settings.overrides['SCHEDULER_DISK_QUEUE'] = 'scrapy.squeue.PickleFifoDiskQueue'
    settings.overrides['SCHEDULER_MEMORY_QUEUE'] = 'scrapy.squeue.FifoMemoryQueue'
    #=====================================================================================================
    settings.overrides['LOG_ENABLED'] = 0
    settings.overrides['DOWNLOAD_DELAY'] = 0.2
    settings.overrides['DEPTH_STATS_VERBOSE'] = 1 #state crawl stats at each depth

    name = "WebOfKnowledge" # Name of the spider, to be used when crawling
    allowed_domains = ['apps.webofknowledge.com'] # Where the spider is allowed to go
   # start_urls = [
   #		'http://apps.webofknowledge.com/summary.do?SID=3AGZik6K471NtVtUjgC&product=WOS&qid=1&search_mode=GeneralSearch'
   #		]
    #rules in plain english: ALLOW: cited or citing articles
    #			     DENY: translating page to chinese, 
    #				   Citation Report, and 
    #				   any more than the 10 most recent papers for each author    

    rules = [Rule(SgmlLinkExtractor(allow=(     #'page=\d+',
	     					#'/CitingArticles\.do\?',
	     					#'/CitedRefList\.do\?',
						'search_mode=CitingArticles',
						'search_mode=CitedRefList',
	     					'/CitedFullRecord\.do\?',
						'/full_record\.do\?'
					   ),
				    deny=(	'\.do\?locale=',
						'/CitationReport\.do\?',
						'search_mode=GeneralSearch')),
				    follow=True, 
				    callback='parse_papers')
		]
    #Put URL in command like with: -a "http://url..."
    def __init__(self, *args, **kwargs): 
      super(WebOfKnowledgeSpider, self).__init__(*args, **kwargs) 
      self.start_urls = [kwargs.get('start_url')] 

	#parsing each page for paper title, authors, and parents
    def parse_papers(self, response):
        hxs = HtmlXPathSelector(response) # The XPath selector
        titles = hxs.select('//div/a[contains(@class, "smallV110")]')
	all_authors = hxs.select('//div/span[contains(text(),"Author(s):")]')
        items = []
        for title in titles:
            item = WebOfKnowledgeItem()
            item['title'] = title.select('value[contains(@lang_id,"")]/text()').extract()
	    #if site.select ('//div/span[contains(@class,"label")]/text()').extract() == "Author(s): "
            # item['authors'] = authors[i].select('/text()').extract()
            item['parent'] = title.select('//span[contains(@class,"parent_biblio")]/span[contains(@class,"summary_data")]/span[contains(@class,"smallV110")]/text()').extract()
	    item['parent_type'] = title.select('//td[contains(@class,"SummTitle")]/p[contains(@class,"NEWpageTitle")]/text()').extract()
            items.append(item)
	for i in range(len(items)):
	    authors = ''.join(all_authors[i].select('../text()').extract())
	    if len(authors.rsplit(';'))>1:
	        authors = authors.rsplit(";")
	    else: authors = [authors]

	    items[i]['authors']=authors	
	    items[i]['authors'].extend(all_authors[i].select('../span[contains(@class,"hitHilite")]/text()').extract())    

	if items == []:#check if we are in a "CitedRef" page
	    titles = hxs.select('//span[contains(@class, "label") and contains(text(),"Title:")]')
	    all_authors = hxs.select('//div/span[contains(text(),"Author(s):")]')
            items = []
            for title in titles:
                item = WebOfKnowledgeItem()
                item['title'] = title.select('../a/span/value/text()').extract()
                item['parent'] = title.select('//span[contains(@class,"parent_biblio")]/span[contains(@class,"summary_data")]/span[contains(@class,"smallV110")]/text()').extract()
                item['parent_type'] = title.select('//td[contains(@class,"SummTitle")]/p[contains(@class,"NEWpageTitle")]/text()').extract()
                items.append(item)
            for i in range(len(items)):
                authors = ''.join(all_authors[i].select('../text()').extract())
		if len(authors.rsplit(';'))>1:
                    authors = authors.rsplit(";")
		else: authors = [authors]
                items[i]['authors']=authors
                items[i]['authors'].extend(all_authors[i].select('../span[contains(@class,"hitHilite")]/text()').extract())

	#else we are in the "full_record" page, and thus there is nothing to extract	
	return items

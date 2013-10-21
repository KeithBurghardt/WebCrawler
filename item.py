from scrapy.item import Item, Field
class WebOfKnowledgeItem(Item):
    '''
    Class for the item retrieved by scrapy.
    '''
    # Here are the fields that will be crawled and stored
    title = Field() # paper title
    authors = Field()  # authors
    cites = Field() #what papers this paper cites
    cited_by = Feild() #what papers are cited by this paper

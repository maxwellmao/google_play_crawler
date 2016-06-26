# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class CrawlerItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class AppCategoryItem(Item):
    name = Field()
    url = Field()
    
class AppItem(Item):
    name = Field()
#    screenShots = Field()
    description = Field()
    trans_desc=Field()
    rating = Field()
#    votes = Field()
#    image = Field()
#    price = Field()
#    category = Field()
#    author = Field()
#    contentRating = Field()
#    fileSize = Field()
#    version = Field()
#    datePublished = Field()
#    package = Field()
    url=Field()
    score=Field()
    ratingValue=Field()
    ratingCount=Field()
#    body=Field()
    trans_desc=Field()
    updated=Field()
    size=Field()
    installs = Field()
    current_version=Field()
    requires_android=Field()
    content_rating=Field()
    contact_developer=Field()
    permissions=Field()
    report=Field()
    price=Field()
    rating_one=Field()
    rating_two=Field()
    rating_three=Field()
    rating_four=Field()
    rating_five=Field()

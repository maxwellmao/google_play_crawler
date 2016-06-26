from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from crawler.items import AppCategoryItem,AppItem

class GooglePlaySpider(CrawlSpider):
    name = "googleplay"
    allowed_domains = ["play.google.com"]
    start_urls = [
        "https://play.google.com/store/apps"
    ]
   
    rules = (
        Rule(SgmlLinkExtractor(allow=('/store/apps$', )), callback='parseCategoryGroup',follow=True),
        Rule(SgmlLinkExtractor(allow=('/store/apps/category/.*', )), callback='parseCategory',follow=True),
        Rule(SgmlLinkExtractor(allow=('/store/search\?.*', )), callback='parseSearch',follow=True),
    )

    def parseCategoryGroup(self, response):
       
        hxs = HtmlXPathSelector(response)
        categoryGroups = hxs.select('//div[@class="padded-content3 app-home-nav"]')

        for categoryGroup in categoryGroups:
           
            categoryGroupName = categoryGroup.select('h2/a/text()').extract()

            categories = categoryGroup.select('ul/li')
            for category in categories:
                categoryName = category.select('a/text()').extract()
                categoryURL = category.select('a/@href').extract()[0]
                print categoryName,categoryURL
               
        import string
        chars = string.ascii_uppercase + string.digits
        for x in chars :
            yield Request('https://play.google.com/store/search?q='+x+'&c=apps',callback=self.parseSearch)
           
        for x in chars :
            for y in chars :
                yield Request('https://play.google.com/store/search?q='+x+y+'&c=apps',callback=self.parseSearch)
               
        for x in chars :
            for y in chars :
                for z in chars :
                    yield Request('https://play.google.com/store/search?q='+x+y+z+'&c=apps',callback=self.parseSearch)
        return
   
    def parseCategory(self,response):   
        basePath = response.url.split('?')[0]   
       
        if '/collection/' in response.url:
            print response.url
            hxs = HtmlXPathSelector(response)
            apps = hxs.select('//a[@class="title"]')
            hasApp = False
            for app in apps:
                hasApp = True
                appName = app.select('text()').extract()
                appURL = app.select('@href').extract()
                print appName,appURL
                yield Request('https://play.google.com'+appURL[0] ,callback=self.parseApp)
                 
            if hasApp :
                import re
                m = re.match(r'(.*)\?start=(\d+)&num=24',response.url)
                if m is None :
                    startNumber = 24                  
                else:
                    startNumber = int(m.group(2))+24
                    print m.group()
                print startNumber
                yield Request(basePath+'?start='+str(startNumber)+'&num=24',callback=self.parseCategory)

        return
   
    def parseSearch(self,response):
        print 'parse search ----'
        import re
        m = re.match(r'(.*)&start=(\d+)&num=24',response.url)
        if m is None :
            basePath = response.url
            startNumber = 24                  
        else:
            startNumber = int(m.group(2))+24
            basePath = m.group(1)
       
        hxs = HtmlXPathSelector(response)
        apps = hxs.select('//a[contains(@href,"/store/apps/details")]')
        hasApp = False
        for app in apps:
            hasApp = True
            appURL = app.select('@href').extract()
            yield Request('https://play.google.com'+appURL[0] ,callback=self.parseApp)
            
        if hasApp:
            print 'next search -----'
            yield Request(basePath+'&start='+str(startNumber)+'&num=24',callback=self.parseSearch)

        return
   
    def parseApp(self,response):

        hxs = HtmlXPathSelector(response)
 
        item = AppItem()
        item['url']=response.url
        item['name']=hxs.select('//div[@class="document-title"]/div[1]/text()').extract()
        print '[Name]', hxs.select('//div[@class="document-title"]/div[1]/text()').extract()
        for info in hxs.xpath('//div[@class="meta-info"]'):
            text_list=info.xpath('div[@class="title"]/text()').extract()
            if text_list:
                t=text_list[0].strip().replace(' ', '_').lower()
                if t=='contact_developer':
                    item[t]=[link.xpath('@href').extract()[0] for link in info.xpath('div[@class="content contains-text-link"]/a[@href]')]
                else:
                    item[t]=[c.strip() for c in info.xpath('div[@class="content"]/text()').extract()]

        price_button=hxs.xpath('//button[@class="price buy"]')
        item['price']=[c.strip() for c in price_button.xpath('span[2]/text()').extract()]
        item['ratingValue']=[c.strip() for c in hxs.select('//meta[@itemprop="ratingValue"]/@content').extract()]
        item['ratingCount']=[c.strip() for c in hxs.select('//meta[@itemprop="ratingCount"]/@content').extract()]
        item['score']=hxs.select('//div[@class="score"]/text()').extract()
    
        rating_histogram=hxs.xpath('//div[@class="rating-histogram"]')
        item['rating_five']=rating_histogram.xpath('div[1]/span[last()]/text()').extract()
        item['rating_four']=rating_histogram.xpath('div[2]/span[last()]/text()').extract()
        item['rating_three']=rating_histogram.xpath('div[3]/span[last()]/text()').extract()
        item['rating_two']=rating_histogram.xpath('div[4]/span[last()]/text()').extract()
        item['rating_one']=rating_histogram.xpath('div[5]/span[last()]/text()').extract()

        item['trans_desc']=hxs.select('//div[@class="id-app-translated-desc"]/descendant-or-self::node()').extract()
        item['description'] = hxs.select('//div[@class="id-app-orig-desc"]//descendant-or-self::node()').extract()
        yield item

        recs = hxs.select('//div[@class="rec-cluster"]')
        for rec in recs:
            apps=rec.select('//a[@class="title" and contains(@href,"/store/apps/details?id=")]')
            for app in apps:
                appURL = app.select('@href').extract()
                if appURL[0].startswith('/store/apps/details?id='):
                    yield Request('https://play.google.com'+appURL[0] ,callback=self.parseApp)

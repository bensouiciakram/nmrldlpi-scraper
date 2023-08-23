import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess 
from scrapy import Request 
from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from scrapy import Request 
from scrapy.shell import inspect_response


class InfosSpider(scrapy.Spider):
    name = 'extractor'  

    headers = {
        "authority": "nmrldlpi.my.site.com",
        "accept": "*/*",
        "accept-language": "en-DZ,en;q=0.9,ar-DZ;q=0.8,ar;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://nmrldlpi.my.site.com",
        "referer": "https://nmrldlpi.my.site.com/bcd/s/rld-public-search?language=en_US",
        "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "x-sfdc-lds-endpoints": "ApexActionController.execute:RLDLicenseSearchController.onSearch",
        "x-sfdc-page-scope-id": "575efceb-3012-4db9-867e-e5fc40e8a433",
        "x-sfdc-request-id": "219376000000388421"
    }
    body = 'message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22160%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FApexActionController%2FACTION%24execute%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22namespace%22%3A%22%22%2C%22classname%22%3A%22RLDLicenseSearchController%22%2C%22method%22%3A%22onSearch%22%2C%22params%22%3A%7B%22professionValue%22%3A%22Board%20of%20Dental%20Health%20Care%22%2C%22licenseTypeValue%22%3A%22Dentist%22%2C%22licenseHolderNameValue%22%3A%22{license_holder_name}%22%2C%22licenseNumberValue%22%3A%22%22%2C%22licenseStatusValue%22%3A%22%22%2C%22cityValue%22%3A%22%22%2C%22countyValue%22%3A%22%22%2C%22stateValue%22%3A%22%22%2C%22zipCodeValue%22%3A%22%22%7D%2C%22cacheable%22%3Afalse%2C%22isContinuation%22%3Afalse%7D%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22MlRqRU5YT3pjWFRNenJranFOMWFjQXlMaWFpdmxPSTZWeEo0bWtiN0hsaXcyNDQuMjAuNC0yLjQxLjQ%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%222L0JGxcI-Ap-Okf-PqAa0Q%22%2C%22COMPONENT%40markup%3A%2F%2FforceCommunity%3AmultiLevelNavigation%22%3A%22bGzlr6loEvLEdn74HlY9AQ%22%2C%22COMPONENT%40markup%3A%2F%2Finstrumentation%3Ao11ySecondaryLoader%22%3A%22WAlywPtXLxVWA9DxV-jd3A%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D&aura.pageURI=%2Fbcd%2Fs%2Frld-public-search%3Flanguage%3Den_US&aura.token=null'
    endpoint = 'https://nmrldlpi.my.site.com/bcd/s/sfsites/aura?r=7&aura.ApexAction.execute=1'

    def start_requests(self):
        yield Request(
            self.endpoint,
            method='POST',
            callback=self.parse_listing,
            headers=self.headers,
            body=self.body.format(
                license_holder_name='SMI'
            )
        )

    def parse_listing(self,response):
        individuals_objs = response.json()['actions'][0]['returnValue']['returnValue']
        for individual_obj in individuals_objs:
            item = {}
            item['License Holder Name'] = individual_obj.get('License_Holder_Name__c')
            item['License Type'] = individual_obj.get('Regulatory_Authorization_Type_Name__c')
            item['License Number'] = individual_obj.get('Name')
            item['License Status'] = individual_obj.get('Status')
            item['Temporary'] = 'Yes' if individual_obj.get('TemporaryLicense__c') else 'No'
            item['Issue Date'] = individual_obj.get('PeriodStart').split('T')[0]
            item['Expiration Date'] = individual_obj.get('periodEnd__c')
            item['Address'] = ' '.join(
                [
                    individual_obj.get('License_Holder_Street__c') if individual_obj.get('License_Holder_Street__c') else '',
                    individual_obj.get('License_Holder_City__c') if individual_obj.get('License_Holder_City__c') else '',
                    individual_obj.get('License_Holder_Postal_Code__c') if individual_obj.get('License_Holder_Postal_Code__c') else '',
                    individual_obj.get('License_Holder_State__c') if individual_obj.get('License_Holder_State__c') else ''
                ]
            )
            item['County'] = individual_obj.get('Licensee_County__c')
            yield item 


process = CrawlerProcess(
    {
        #'LOG_LEVEL':'ERROR',
        'CONCURENT_REQUESTS':4,
        'DOWNLOAD_DELAY':0.5,
        'HTTPCACHE_ENABLED' : True,
        'FEED_URI':'output.csv',
        'FEED_FORMAT':'csv',
    }
)
process.crawl(InfosSpider)
process.start()

from ..items import DigiskolaWebsiteScraperItem
import scrapy
import re
import pandas as pd


class NewsCrawlerSpider(scrapy.Spider):
    name = "news_crawler"
    allowed_domains = ["detik.com"]
    start_urls = ["https://detik.com/"]
    scraped_data = []
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    def parse(self, response):
        articles = response.xpath('//article[@class="list-content__item"]')
        for article in articles:
            
            item = DigiskolaWebsiteScraperItem()
            item['title'] = article.xpath('.//h3[@class="media__title"]/a/text()').get()
            item['news_link'] = article.xpath('.//a[@class="media__link"]/@href').get()
            item['news_date'] = article.xpath('.//div[@class="media__date"]/span/@title').get()
            yield item
           
            # Append scraped data to the list and clean text
            self.scraped_data.append({
                'title': self.clean_text(item['title']),
                'news_link': self.clean_text(item['news_link']),
                'news_date': self.clean_text(item['news_date'])
            })
       
        # Follow pagination if there's a "next page" link
        next_page = response.xpath('//a[@class="pagination__next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def clean_text(self, text):
        # Function to remove double quotes from the scraped text
        if text:
            cleaned_text = re.sub(r'"|\n', '', text)
            return cleaned_text.strip()  # Remove leading/trailing spaces as well

        else:
            return text
    
    def closed(self, reason):
        # Create a DataFrame from the scraped data
        df = pd.DataFrame(self.scraped_data)

        # Write the DataFrame to a CSV file
        df.to_csv('news_data.csv', index=False, encoding='utf-8')
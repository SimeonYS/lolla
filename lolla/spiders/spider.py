import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import LollaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class LollaSpider(scrapy.Spider):
	name = 'lolla'
	start_urls = ['https://www.lollandsbank.dk/presse-nyheder/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="entry-content"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//time[contains(@class,"entry-date published")]/text()').get()
		title = response.xpath('//div[@class="headline"]/h1/text()').get()
		content = response.xpath('//div[@class="entry-content"]//text()[not (ancestor::span[@class="posted-on"]) and not (ancestor::span[@class="byline"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=LollaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

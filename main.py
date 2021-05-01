from Scraper import TopicScrapper
import json

scraper = TopicScrapper()
scraper.get_topic(['javascript'], 'ru')

with open('topics.json', 'w', encoding='utf-8') as json_file:
    json.dump(scraper.topics, json_file, ensure_ascii=False)
json_file.close()
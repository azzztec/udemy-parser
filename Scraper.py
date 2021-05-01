import requests
import config as cnf
import time
from bs4 import BeautifulSoup
from selenium import webdriver
config = cnf.config

class TopicScrapper:
    def __init__(self):
        self.topics = []

    def get_topic(self, topics, lang):
        for topic in topics:
            topic_courses = []
            avarage_students = 0
            topic_html = self._get_topic_html(self._create_topic_link(topic, lang, 1))
            page_count = self._get_topic_pages_number(topic_html)
            for current_page_number in range(0, page_count):
                topic_html = self._get_topic_html(self._create_topic_link(topic, lang, current_page_number + 1))
                (current_page_courses, avarage_students_on_page) = self._scrap_courses(topic_html)
                topic_courses += current_page_courses
                avarage_students += avarage_students_on_page
            self.topics.append({
                'topic_name': topic,
                'topic_info': [{
                    'lang': lang,
                    'avarage_stidents': avarage_students,
                    'courses': topic_courses
                }]
            })

    def _scrap_courses(self, topic_html):
        courses = []
        avarage_students = 0
        soup = BeautifulSoup(topic_html, 'lxml')
        topic_courses_divs = soup.find_all('div', attrs={'class': 'popper--popper--19faV'})
        courses_endpoints = self._get_courses_endpoints_in_topic(topic_courses_divs)
        for course_endpoint in courses_endpoints:
            course_html = requests.get(self._create_course_link(course_endpoint), headers=config['HEADERS'], params='')
            soup = BeautifulSoup(course_html.text, 'lxml')
            course_title_html = soup.find('h1', attrs={'class': 'udlite-heading-xl'})
            students_amount_html = soup.find('div', attrs={'data-purpose': 'enrollment'})
            if course_title_html and students_amount_html:
                student_number = int(''.join([s for s in students_amount_html.text.split() if s.isdigit()]))
                avarage_students += student_number
                courses.append({
                    'title': course_title_html.text,
                    'students': student_number
                })
        return (courses, avarage_students)

    def _create_topic_link(self, topic_name, lang, page_number):
        return  config['TOPIC_URL'] + config['LANG_SEARCH'] + lang + config['PAGE_NUMBER_SEARCH'] + str(page_number) + config['TOPIC_SEARCH'] + topic_name + config['URL_QUERIES']

    def _create_course_link(self, course_endpoint):
        return config['COURSE_URL'] + course_endpoint

    def _get_topic_html(self, topic_link):
        web_driver = webdriver.Chrome(config['CHROME_DRIVER_LOCATION'])
        web_driver.get(topic_link)
        time.sleep(5)
        html = web_driver.page_source
        web_driver.close()
        return html

    def _get_courses_endpoints_in_topic(self, topics_divs):
        endpoints = []
        for topic_div in topics_divs:
            if topic_div.find('p'):
                endpoints.append(topic_div.find('a')['href'])
        return endpoints

    def _get_topic_pages_number(self, topic_html):
        soup = BeautifulSoup(topic_html, 'lxml')
        pagination = soup.find_all(attrs={'class': 'pagination--page--3FKqV'})
        if not pagination:
            return 1
        return int(pagination[-1].text)
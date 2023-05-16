import datetime
import re
import urllib
from functools import wraps
from celery import shared_task
from .helpers import get_cities
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlparse
import bugsnag
from .models import Account, Tasks, MaxConcurrency, Result
import requests
import dateparser
from django.core.cache import cache

class FacebookScraper:

    def __init__(self, keyword, city, account_id, concurrency_id):
        self.keyword = keyword
        self.city = city
        self.account = Account.objects.get(id=account_id)

        self.username = self.account.username
        self.password = self.account.password
        self.concurrency = MaxConcurrency.objects.get(id=concurrency_id)
        self.options = webdriver.ChromeOptions()
        self.rotate_ip()
        self.options.add_argument("--start-maximized")
        self.options.add_argument(f'--proxy-server=127.0.0.1:{24000+self.concurrency.current_concurrency}')
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-notifications")
        self.driver = webdriver.Chrome(options=self.options)

    def rotate_ip(self):
        requests.get(f'http://127.0.0.1:22999/api/refresh_sessions/{24000+self.concurrency.current_concurrency}')

    def scrape(self):
        print('scrape function started')

        try:
            self.login()
            search_urls = self.get_search_url()
            print(len(search_urls))
            time.sleep(10)
            last_processed_index = 0
            while last_processed_index < len(search_urls):
                current_url = search_urls[last_processed_index]
                try:
                    self.get_data_from_links(current_url)
                    last_processed_index += 1
                except Exception as e:
                    print(f"An error occurred for URL '{current_url}': {str(e)}")
                    print("Retrying in 5 seconds...")
                    time.sleep(5)

            # for search_url in search_urls:
            #     self.get_data_from_links(search_url)
        except Exception as e:
            self.account.is_used = False
            self.account.save()
            self.concurrency.current_concurrency -= 1
            self.concurrency.save()
            print(e)
            bugsnag.notify(e)
            try:
                self.driver.quit()
            except:
                pass
            return
        try:
            self.driver.quit()
        except:
            pass
        self.account.is_used = False
        self.account.save()
        self.concurrency.current_concurrency -= 1
        self.concurrency.save()

    def login(self):
        login_url = 'https://www.facebook.com/login.php'
        self.driver.get(login_url)
        email_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'email'))
        )

        email_field.send_keys(self.username)
        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'pass'))
        )
        password_field.send_keys(self.password)
        password_field.submit()
        time.sleep(10)

    def get_search_url(self):
        self.driver.get(f'https://www.facebook.com/search/pages/?q={urllib.parse.quote_plus(self.keyword)}')
        self.driver.find_element(By.CSS_SELECTOR,
                                 'div.x9f619.x78zum5.xurb0ha.x1y1aw1k.xwib8y2.x1yc453h.xh8yej3 > div > span > span').click()
        time.sleep(1)
        print(self.city)
        self.driver.find_element(By.XPATH, '//input[@aria-label="Location"]').send_keys(self.city)
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, 'div.x78zum5.xdt5ytf.x1l1ennw.x6ikm8r > div > span > span').click()
        time.sleep(5)
        self.scroll_down()
        html = self.driver.page_source

        # parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        a_tags = soup.find_all("a", {"role": "presentation"})
        links = []
        for a_tag in a_tags:
            href = a_tag.get("href")
            links.append(href)
        unique_links = list(set(links))
        print(unique_links)
        return unique_links

    def scroll_down(self):

        # Get scroll height.
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:

            # Scroll down to the bottom.
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page.
            time.sleep(4)

            # Calculate new scroll height and compare with last scroll height.
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

    def get_data_from_links(self, url):
        #, cron jobs
        self.driver.get(url)
        time.sleep(5)
        info = {}
        info['url'] = url
        info['city'] = self.city
        info['keyword'] = self.keyword
        try:
            info['title'] = self.driver.find_element(By.CSS_SELECTOR,
                                                 'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x1cy8zhl.xexx8yu > div > div > span > h1').text
        except NoSuchElementException:
            return
        try:
            info['phone'] = self.driver.find_element(By.CSS_SELECTOR,
                                                     'div:nth-child(3) > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div > div > span').text
        except NoSuchElementException:
            pass
        try:
            info['address'] = self.driver.find_element(By.CSS_SELECTOR,
                                                       'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div > span').text
        except NoSuchElementException:
            pass
        try:
            info['category'] = self.driver.find_element(By.CSS_SELECTOR,
                                                     'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div > div > span > div > span').text.strip(
                'Page · ')
        except NoSuchElementException:
            try:
                info['category'] = self.driver.find_element(By.CSS_SELECTOR, 'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div > div > span > span > a > span').text
            except NoSuchElementException:
                pass
        try:
            info['followers'] = self.driver.find_element(By.CSS_SELECTOR,
                                                     'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x2lah0s.x193iq5w.x1cy8zhl.xyamay9 > span > a:nth-child(2)').text.strip(
                ' followers')
        except NoSuchElementException:
            pass
        try:
            info['email'] = self.driver.find_element(By.CSS_SELECTOR,
                                                     'div.xieb3on > div:nth-child(2) > div > ul > div:nth-child(4) > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div > div > span').text
            if '@' not in info['email']:
                info['email'] = ''
        except NoSuchElementException:
            pass
        try:
            info['website'] = self.driver.find_element(By.CSS_SELECTOR,
                                                       'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div > a > div > div > span').text
        except NoSuchElementException:
            pass
        try:
            info['rating'] = self.driver.find_element(By.CSS_SELECTOR, 'div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > a > div > div > span').text.strip('Rating · ')
        except NoSuchElementException:
            pass
        try:
            info['instagram_url'] = self.driver.find_element(By.CSS_SELECTOR, "a[href*='instagram.com']").get_attribute('href')
        except NoSuchElementException:
            pass
        try:
            info['page_created'] = dateparser.parse(self.driver.find_element(By.CSS_SELECTOR, 'div.x7wzq59 > div:nth-child(4) > div > div > div > span > div.x1hmvnq2 > span').text.strip('Page created – '))
            info['page_id'] = re.findall(self.driver.page_source, r'page_id=([^"]+)"')[0]
        except NoSuchElementException:
            self.driver.find_element(By.XPATH, '//span[text()="About"]').click()
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//span[text()="Page transparency"]').click()
            time.sleep(10)
            info['page_created'] = dateparser.parse(self.driver.find_element(By.CSS_SELECTOR, 'div:nth-child(3) > div > div > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div.xzsf02u.x6prxxf.xvq8zen.x126k92a.x12nagc > span').text)
            info['page_id'] = self.driver.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > div > div > div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.xdt5ytf.x193iq5w.xeuugli.x1r8uery.x1iyjqo2.xs83m0k.xamitd3.xsyo7zv.x16hj40l.x10b6aqq.x1yrsyyn > div.xzsf02u.x6prxxf.xvq8zen.x126k92a.x12nagc > span').text

        queryset = Result.objects.filter(page_id=info['page_id'])
        if queryset:
            queryset.update(**info)
        else:
            Result.objects.create(**info)
        time.sleep(5)


def skip_if_running(f):
    task_name = f'{f.__module__}.{f.__name__}'

    @wraps(f)
    def wrapped(self, *args, **kwargs):
        workers = self.app.control.inspect().active()

        for worker, tasks in workers.items():
            for task in tasks:
                if (task_name == task['name'] and
                        tuple(args) == tuple(task['args']) and
                        kwargs == task['kwargs'] and
                        self.request.id != task['id']):
                    print(f'task {task_name} ({args}, {kwargs}) is running on {worker}, skipping')

                    return None

        return f(self, *args, **kwargs)

    return wrapped


@shared_task
def main(city, keyword, account_id, concurrency_id):
    print('main function started')
    scraper = FacebookScraper(city=city, keyword=keyword, account_id=account_id, concurrency_id=concurrency_id)
    scraper.scrape()


@shared_task(bind=True)
@skip_if_running
def get_facebook_data(self):
    for task in Tasks.objects.filter(next_execution__lte=datetime.datetime.now()):
        city_list = get_cities(task.file.path)
        print(len(city_list))
        task.next_execution = datetime.datetime.now() + datetime.timedelta(minutes=task.run_every_minutes)
        task.task_progress = 'in_progress'
        task.save()

        for city in city_list:

            cache_key = f"{city}_{task.keyword}"


            print(city)
            if cache.get(cache_key):
                print(f"City {city} with keyword {task.keyword} is already cached. Skipping scraping.")
            else:

                while True:
                    print('concurrency')

                    concurrency = MaxConcurrency.objects.all().first()
                    if concurrency.max_concurrency <= concurrency.current_concurrency:
                        time.sleep(10)
                    else:
                        concurrency.current_concurrency += 1
                        concurrency.save()
                        break
                while True:
                    print('account')
                    if not Account.objects.filter(is_used=False):
                        time.sleep(10)
                    else:
                        account = Account.objects.filter(is_used=False).first()
                        account.is_used = True
                        account.save()
                        break
                print('task started')
                main.delay(city, task.keyword, account.id, concurrency.id)
                cache_time = task.cache_time * 60
                cache.set(cache_key, True, cache_time)
                print(f"City {city} with keyword {task.keyword} scraped and added to cache.")
        task.task_progress = 'finished'


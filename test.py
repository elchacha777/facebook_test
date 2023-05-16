# # import requests
# # from bs4 import BeautifulSoup
# #
# # response = requests.get('https://www.facebook.com/docravipattar')
# # html = response.content
# # soup = BeautifulSoup(response.text, 'html.parser')
# #
# #
# # soup = BeautifulSoup(html, 'html.parser')
# #
# # # Extract the data you want using BeautifulSoup selectors
# # profile_name = soup.select_one('h1#fb-timeline-cover-name > span').text
# # about_section = soup.select_one('div#pagelet_timeline_medley_about')
# # about_text = about_section.select_one('div._4bl9').text
# # print(profile_name)
#
# # from facebook_scraper import get_profile
# # print(get_profile("zuck"))
#
#
#
# import time
#
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
#
#
#
# class FacebookScraper:
#     USERNAME = 'zver.cm@gmail.com'
#     PASSWORD = '6253350q'
#     URL = 'https://www.facebook.com/docravipattar'
#
#
#     def __init__(self):
#         self.options = webdriver.ChromeOptions()
#         self.options.add_argument("--start-maximized")
#         self.options.add_argument("--disable-infobars")
#         self.options.add_argument("--disable-extensions")
#         self.options.add_argument("--disable-notifications")
#         self.driver = webdriver.Chrome(options=self.options)
#
#
#     def get_page(self):
#         self.driver.get(FacebookScraper.URL)
#         resp = self.driver.page_source
#         soup = BeautifulSoup(resp, 'html.parser')
#
#         items = soup.find_all('div', {
#             'class': 'x9f619 x1n2onr6 x1ja2u2z x78zum5 x2lah0s x1qughib x1qjc9v5 xozqiw3 x1q0g3np x1pi30zi x1swvt13 xyamay9 xykv574 xbmpl8g x4cne27 xifccgj'})[1]
#         print(items)
#         allDetails = items.find_all("div", {
#             "class": "x9f619 x1n2onr6 x1ja2u2z x78zum5 x2lah0s x1nhvcw1 x1qjc9v5 xozqiw3 x1q0g3np xyamay9 xykv574 xbmpl8g x4cne27 xifccgj"})
#         print(allDetails)
#         for contact in allDetails:
#             print(contact)
#
#
#
# scraper = FacebookScraper()
# scraper.get_page()
# time.sleep(10)


import csv

def get_cities(file_path):
    city_list = []
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            city = row['city']
            state_name = row['state_name']
            if 'St.' in city:
                city = city.replace('St.', 'Saint')
            city_list.append(f'{city}, {state_name}')
    print(city_list)
    return city_list

get_cities()

# -*- coding: utf-8 -*-
from argparse import Namespace
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time
import traceback
import numpy as np
import itertools

from customlogger import get_logger
from dateutils import parse_relative_date

GM_WEBPAGE = 'https://www.google.com/maps/'
MAX_WAIT = 10
MAX_RETRY = 5
MAX_SCROLLS = 40

class GoogleMapsScraper:

    def __init__(self, debug=False):
        self.debug = debug
        self.logger = get_logger('scraper')
        self.driver = self.__get_driver()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            self.logger.exception(exc_value)

        self.driver.close()
        self.driver.quit()

        return True

    def sort_by(self, url, ind):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, MAX_WAIT)

        # open dropdown menu
        clicked = False
        tries = 0
        while not clicked and tries < MAX_RETRY:
            try:
                #if not self.debug:
                #    menu_bt = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cYrDcjyGO77__container')))
                #else:
                wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@jsaction="pane.rating.moreReviews"] | //button[@jsaction="pane.reviewChart.moreReviews"]'))).click()
                                                                            
                menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Mais relevantes"] | //button[@aria-label="Classificar avaliações"]')))
                menu_bt.click()

                clicked = True
                time.sleep(3)
            except Exception:
                tries += 1
                self.logger.warn('Failed to click sorting button ' + url)

            # failed to open the dropdown
            if tries == MAX_RETRY:
                return -1

        #  element of the list specified according to ind
        recent_rating_bt = self.driver.find_elements(By.XPATH, '//li[@role=\'menuitemradio\']')[ind]
        recent_rating_bt.click()

        # wait to load review (ajax call)
        time.sleep(5)

        return 0

    def get_places(self, method='urls', keyword_list=None):

        df_places = pd.DataFrame()

        if method == 'urls':
            # TODO:
            # search_point_url = row['url']  
            pass
        if method == 'squares':
            search_point_url_list = self._gen_search_points_from_square(keyword_list=keyword_list)
        else:
            # search_point_url = f"https://www.google.com/maps/search/{row['keyword']}/@{str(row['longitude'])},{str(row['latitude'])},{str(row['zoom'])}z"
            # TODO:
            pass

        for i, search_point_url in enumerate(search_point_url_list):

            if (i+1) % 10 == 0:
                print(f"{i}/{len(search_point_url_list)}")
                df_places = df_places[['search_point_url', 'href', 'name', 'rating', 'num_reviews', 'close_time', 'other']]
                df_places.to_csv('output/places_wax.csv', index=False)


            try:
                self.driver.get(search_point_url)
            except NoSuchElementException:
                self.driver.quit()
                self.driver = self.__get_driver()
                self.driver.get(search_point_url)

            # Gambiarra to load all places into the page
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR,
                "div.siAUzd-neVct.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc > div[aria-label*='Results for']")
            for i in range(10):
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)

            # Get places names and href
            # time.sleep(2)
            response = BeautifulSoup(self.driver.page_source, 'html.parser')
            div_places = response.select('div[jsaction] > a[href]')
            # print(len(div_places))
            for div_place in div_places:
                place_info = {
                    'search_point_url': search_point_url.replace('https://www.google.com/maps/search/', ''),
                    'href': div_place['href'],
                    'name': div_place['aria-label'],
                    'rating': None,
                    'num_reviews': None,
                    'close_time': None,
                    'other': None
                }

                df_places = df_places.append(place_info, ignore_index=True)
        df_places = df_places[['search_point_url', 'href', 'name', 'rating', 'num_reviews', 'close_time', 'other']]
        df_places.to_csv('output/places_wax.csv', index=False)
        self.driver.quit()

    def _gen_search_points_from_square(self, keyword_list=None):
        # TODO: Generate search points from corners of square

        keyword_list = [] if keyword_list is None else keyword_list

        square_points = pd.read_csv('input/square_points.csv')

        cities = square_points['city'].unique()

        search_urls = []

        for city in cities:

            df_aux = square_points[square_points['city'] == city]
            latitudes = np.linspace(df_aux['latitude'].min(), df_aux['latitude'].max(), num=20)
            longitudes = np.linspace(df_aux['longitude'].min(), df_aux['longitude'].max(), num=20)
            coordinates_list = list(itertools.product(latitudes, longitudes, keyword_list))

            search_urls += [f"https://www.google.com/maps/search/{coordinates[2]}/@{str(coordinates[1])},{str(coordinates[0])},{str(15)}z"
             for coordinates in coordinates_list]

        return search_urls



    def get_reviews(self, writer, args = Namespace()):

        # scroll to load reviews

        # wait for other reviews to load (ajax)
        time.sleep(4)

        self.__scroll()

        # expand review text
        self.__expand_reviews()

        # parse reviews
        response = BeautifulSoup(self.driver.page_source, 'html.parser')
        # TODO: Subject to changes
        rblock = response.find_all('div', class_='jftiEf fontBodyMedium')
        parsed_reviews = []

        for review in rblock:
            parsed = self.__parse(review)
            parsed_reviews.append(parsed)
            if not (args.today and parse_relative_date(parsed['retrieval_date'], parsed['relative_date']) < args.today):
                writer.writerow(parsed.values())
            else:
                self.logger.debug('breaking:\t%s', (parsed['relative_date']))
                return parsed_reviews

        return parsed_reviews


    def get_account(self, url):

        self.driver.get(url)

        # ajax call also for this section
        time.sleep(4)

        resp = BeautifulSoup(self.driver.page_source, 'html.parser')

        place_data = self.__parse_place(resp)

        return place_data


    def __parse(self, review):

        item = {}

        try:
            # TODO: Subject to changes
            id_review = review['data-review-id']
        except Exception:
            id_review = None
    
        try:
            # TODO: Subject to changes
            username = review['aria-label']
        except Exception:
            username = None
    
        try:
            # TODO: Subject to changes
            review_text = self.__filter_string(review.find('span', class_='wiI7pd').text)
        except Exception:
            review_text = None

        try:
            # TODO: Subject to changes
            rating_arr = review.find('span', class_='kvMYJc')
            rating_str = '-1'
            if rating_arr and rating_arr.get('aria-label'):
                rating_str = rating_arr['aria-label'].split(' ')[1]
            else:
                rating_str = review.find('span', class_='fzvQIb').text.strip().split('/')[0]
            rating = int(rating_str)
                
        except Exception:
            rating = None

        try:
            # TODO: Subject to changes
            relative_date = review.find('span', class_='xRkPPb').find('span').text.strip()
        except Exception:
            relative_date = None        

        # try:
        #     n_reviews_photos = review.find('div', class_='section-review-subtitle').find_all('span')[1].text
        #     metadata = n_reviews_photos.split('\xe3\x83\xbb')
        #     if len(metadata) == 3:
        #         n_photos = int(metadata[2].split(' ')[0].replace('.', ''))
        #     else:
        #         n_photos = 0

        #     idx = len(metadata)
        #     n_reviews = int(metadata[idx - 1].split(' ')[0].replace('.', ''))

        # except Exception as e:
        #     n_reviews = 0
        #     n_photos = 0

        try:
            user_url = review.find('a')['href']
        except Exception:
            user_url = None

        item['id_review'] = id_review
        item['caption'] = review_text

        # depends on language, which depends on geolocation defined by Google Maps
        # custom mapping to transform into date should be implemented
        item['relative_date'] = relative_date

        # store datetime of scraping and apply further processing to calculate
        # correct date as retrieval_date - time(relative_date)
        item['retrieval_date'] = datetime.now()
        item['rating'] = rating
        item['username'] = username
        item['n_review_user'] = 0
        # n_reviews
        item['n_photo_user'] = 0
        # n_photos
        item['url_user'] = user_url

        return item


    def __parse_place(self, response):

        place = {}
        try:
            place['overall_rating'] = float(response.find('div', class_='gm2-display-2').text.replace(',', '.'))
        except Exception:
            place['overall_rating'] = 'NOT FOUND'

        try:
            place['n_reviews'] = int(response.find('div', class_='gm2-caption').text.replace('.', '').replace(',','').split(' ')[0])
        except Exception:
            place['n_reviews'] = 0

        return place

    # expand review description
    def __expand_reviews(self):
        # use XPath to load complete reviews
        # TODO: Subject to changes
        links = self.driver.find_elements(By.XPATH, '//button[@jsaction="pane.review.expandReview"]')
        for l in links:
            l.click()
        time.sleep(2)


    def __scroll(self):
        # TODO: Subject to changes
        scrollable_div = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
        self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def __get_driver(self):
        self.logger.info('iniciando webdriver')
        options = webdriver.ChromeOptions()

        if not self.debug:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=1366,768")

        options.add_argument("--disable-notifications")
        options.add_argument("--lang=en-GB")
        input_driver = webdriver.Remote("http://localhost:4444/wd/hub", DesiredCapabilities.CHROME, options=options)
        self.logger.info('webdriver carregado')

        # first lets click on google agree button so we can continue
        try:
            input_driver.get(GM_WEBPAGE)
            agree = WebDriverWait(input_driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "I agree")]')))
            agree.click()

            # back to the main page
            input_driver.switch_to_default_content()
        except Exception:
            pass

        return input_driver


    # util function to clean special characters
    def __filter_string(self, str):
        return str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

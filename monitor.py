#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from pymongo import MongoClient
import argparse
import logging

DB_URL = 'mongodb://localhost:27017/'
DB_NAME = 'googlemaps'
COLLECTION_NAME = 'review'

class Monitor:

    def __init__(self, mongourl=DB_URL):

        # define MongoDB connection
        self.client = MongoClient(mongourl)

        # min date review to scrape
        # self.min_date_review = datetime.strptime(from_date, '%Y-%m-%d')

        # logging
        self.logger = self.__get_logger()
    
    def save_review(self, file_url):
        # set connection to DB
        collection = self.client[DB_NAME][COLLECTION_NAME]

        with open(file_url, newline='') as csvfile:
            spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for r in spamreader:
                print(r)
                # calculate review date and compare to input min_date_review
                # r['timestamp'] = self.__parse_relative_date(r['relative_date'])
                # collection.insert_one(r)

    # def scrape_gm_reviews(self):
    #     # set connection to DB
    #     collection = self.client[DB_NAME][COLLECTION_NAME]

    #     # init scraper and incremental add reviews
    #     # TO DO: pass logger as parameter to log into one single file?
    #     with GoogleMapsScraper() as scraper:
    #         for url in self.urls:
    #             try:
    #                 error = scraper.sort_by_date(url)
    #                 if error == 0:
    #                     stop = False
    #                     offset = 0
    #                     n_new_reviews = 0
    #                     while not stop:
    #                         rlist = scraper.get_reviews(offset)
    #                         for r in rlist:
    #                             # calculate review date and compare to input min_date_review
    #                             r['timestamp'] = self.__parse_relative_date(r['relative_date'])
    #                             stop = self.__stop(r, collection)
    #                             if not stop:
    #                                 collection.insert_one(r)
    #                                 n_new_reviews += 1
    #                             else:
    #                                 break
    #                         offset += len(rlist)

    #                     # log total number
    #                     self.logger.info('{} : {} new reviews'.format(url, n_new_reviews))
    #                 else:
    #                     self.logger.warning('Sorting reviews failed for {}'.format(url))

    #             except Exception as e:
    #                 exc_type, exc_obj, exc_tb = sys.exc_info()
    #                 fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    #                 self.logger.error('{}: {}, {}, {}'.format(url, exc_type, fname, exc_tb.tb_lineno))


    # def __stop(self, r, collection):
    #     is_old_review = collection.find_one({'id_review': r['id_review']})
    #     if is_old_review is None and r['timestamp'] >= self.min_date_review:
    #         return False
    #     else:
    #         return True

    def __get_logger(self):
        # create logger
        logger = logging.getLogger('monitor')
        logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        fh = logging.FileHandler('monitor.log')
        fh.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # add formatter to ch
        fh.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(fh)

        return logger


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Monitor Google Maps places')
    parser.add_argument('--file', type=str, default='urls.txt', help='target URLs file')
    # parser.add_argument('--from-date', type=str) # start date in format: YYYY-MM-DD

    args = parser.parse_args()

    monitor = Monitor()

    try:
        monitor.save_reviews(args.file)
    except Exception as e:
        monitor.logger.error('Not handled error: {}'.format(e))

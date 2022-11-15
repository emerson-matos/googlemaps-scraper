# -*- coding: utf-8 -*-
from customlogger import get_logger
from dateutils import parse_relative_date
from googlemaps import GoogleMapsScraper
from multiprocessing import Pool
from termcolor import colored
from datetime import datetime
import argparse
import csv

ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }
HEADER = ['id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']
HEADER_W_SOURCE = ['id_review', 'caption', 'relative_date','retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'url_source']

def csv_writer(source_field, ind_sort_by, path='data/2022/09/20/'):
    outfile= ind_sort_by + '-gm-reviews.csv'
    targetfile = open(path + outfile, mode='a', encoding='utf-8', newline='\n')
    writer = csv.writer(targetfile, quoting=csv.QUOTE_MINIMAL)

    if source_field:
        h = HEADER_W_SOURCE
    else:
        h = HEADER
    writer.writerow(h)

    return writer

def do_the_job(row, args, logger):
    logger.info('doing the job')
    writer = csv_writer(args.source, row['name'].strip().lower().replace(" ", "-"))
    logger.info('writer created')
    with GoogleMapsScraper(args.debug) as scraper:
        url = row['url']
        logger.info('scrapping...')
        error = scraper.sort_by(url, ind[args.sort_by])
        if error == 0:
            n = 0
            logger.info(url)
            logger.info('\t' + url + ' review ' + str(n))
            while n < int(row['limit']):
                reviews = scraper.get_reviews(writer, args)
                n += len(reviews)
                logger.info('\t' + url + ' review ' + str(n))
                if args.today and parse_relative_date(reviews[-1]['retrieval_date'], reviews[-1]['relative_date']) < args.today:
                    n = 999999

def callback(some):
    print(colored("deu bom" + str(some)))

def error_callback(some):
    print(colored("deu ruim" + str(some)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--sort_by', type=str, default='newest', help='most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file (for multiple urls in a single file)')
    parser.add_argument('--processes', type=int, dest='processes', help='Quantity of processes to launch')
    parser.add_argument('--today', dest='today', action='store_const', const=datetime.today().replace(hour=0, minute=0, second=0, microsecond=0), help='limit to scrape only today reviews')
    parser.set_defaults(place=False, debug=False, source=False, processes=4)
    args = parser.parse_args()
    results = []
    logger = get_logger('main')
    try:
        with open(args.i, newline='') as csvfile:
            with Pool(processes=args.processes) as pool:    
                for row in csv.DictReader(csvfile, delimiter=',', quotechar='|'):
                    result = pool.apply_async(do_the_job, (row, args, logger), callback=callback, error_callback=error_callback)
                    results.append(result)
                [result.wait() for result in results]
    except Exception as e:
        logger.exception(e)

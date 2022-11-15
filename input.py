# -*- coding: utf-8 -*-
# import csv

# if __name__ == '__main__':
#     # store reviews in CSV file
#    with open('input.csv', newline='') as csvfile:
#     spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
#     for row in spamreader:
#         print(row)

# -*- coding: utf-8 -*-
# from googlemaps import GoogleMapsScraper
from termcolor import colored
import argparse
import csv
from multiprocessing import Pool, freeze_support

def do_the_job(file_url, debug):
   print(file_url, colored(debug, 'cyan'));
   return file_url

def callback(some):
    print(some, colored("deu bom"));

def error_callback(some):
    print(some, colored("deu ruim"));

def main():
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()
    results = []
    with open("urls.txt", newline='') as csvfile:
        with Pool(processes=4) as pool:    
            for row in csv.DictReader(csvfile, delimiter=',', quotechar='|'):
                url = row['url']
                result = pool.apply_async(do_the_job, (url, args), callback=callback, error_callback=error_callback)
                results.append(result)
            [result.wait() for result in results]
        # pool.apply_async(func=do_the_job, args=[], callback=callback, error_callback=error_callback)

if __name__=="__main__":
    freeze_support()
    main()
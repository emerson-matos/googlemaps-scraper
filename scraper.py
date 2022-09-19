# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
import argparse
import csv
from termcolor import colored


ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }
HEADER = ['id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']
HEADER_W_SOURCE = ['id_review', 'caption', 'relative_date','retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'url_source']

def csv_writer(source_field, ind_sort_by, path='data/2022/09/17/'):
    outfile= ind_sort_by + '-gm-reviews.csv'
    targetfile = open(path + outfile, mode='a', encoding='utf-8', newline='\n')
    writer = csv.writer(targetfile, quoting=csv.QUOTE_MINIMAL)

    if source_field:
        h = HEADER_W_SOURCE
    else:
        h = HEADER
    writer.writerow(h)

    return writer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--sort_by', type=str, default='newest', help='most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file (for multiple urls in a single file)')
    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()

    with GoogleMapsScraper(debug=args.debug) as scraper:
        with open('input.csv', newline='') as csvfile:
            
            for row in csv.DictReader(csvfile, delimiter=',', quotechar='|'):
                    # store reviews in CSV file
                writer = csv_writer(args.source, row['name'].strip().lower().replace(" ", "-"))
                url = row['url']
                error = scraper.sort_by(url, ind[args.sort_by])

                if error == 0:
                    n = 0
                    print(colored(url + ' with ' + row['limit'], 'red'))
                    print(colored('\t' + url + ' review ' + str(n) + ' of ' + row['limit'], 'cyan'))

                    while n < int(row['limit']):

                        reviews = scraper.get_reviews(n)

                        if len(reviews) == 0:
                            break

                        for r in reviews:
                            row_data = list(r.values())
                            if args.source:
                                row_data.append(url[:-1])

                            writer.writerow(row_data)

                        n += len(reviews)
                        print(colored('\t' + url + ' review ' + str(n) + ' of ' + row['limit'], 'cyan'))
        scraper.driver.close()
        scraper.driver.quit()

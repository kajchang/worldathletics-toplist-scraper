import requests
from bs4 import BeautifulSoup

import concurrent.futures
import itertools
import csv
import os
from urllib.parse import urlencode

EVENTS = {
    '60-metres': 'sprints',
    '100-metres': 'sprints',
    '200-metres': 'sprints',
    '400-metres': 'sprints',
    '800-metres': 'middlelong',
    '1500-metres': 'middlelong',
    '3000-metres': 'middlelong',
    '3000-metres-steeplechase': 'middlelong',
    '5000-metres': 'middlelong',
    '10000-metres': 'middlelong'
}

CURRENT_YEAR = 2024

YEARS = range(2001, CURRENT_YEAR + 1)

NUM_PERFORMANCES = 1000

NUM_PAGES = int(NUM_PERFORMANCES / 100)

PAGES = range(1, NUM_PAGES + 1)

AGE_CATEGORY = ['senior'] # 'u18', 'u20'

BEST_RESULTS_ONLY = [True] # False

MAX_RESULTS_BY_COUNTRY = ['all'] # '1', '2', '3', '4', '5'

REGION_TYPE = ['world']

GENDER = ['men', 'women']

def get_top_list(event, environment, gender, age_category, year, event_category, **kwargs):
    event_suffix = '-short-track' if environment == 'indoor' else ''
    url = f'https://worldathletics.org/records/toplists/{event_category}/{event + event_suffix}/all/{gender}/{age_category}/{year}?{urlencode(kwargs)}'

    print(url)

    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'lxml')

    results = []

    records_table = soup.find(class_='records-table')

    if records_table is None:
        return None

    for tr in records_table.find_all('tr')[1:]:
        results.append(tuple(td.text.strip() for td in tr.find_all('td')))

    return results

HEADERS = ['Rank', 'Mark', 'Competitor', 'DOB', 'Nat', 'Pos', '', 'Venue', 'Date', 'ResultScore']

for (year, event, age_category, best_results_only, region_type, gender, max_results_by_country) in itertools.product(YEARS, filter(lambda e: e != '100-metres' and e != '10000-metres' and e != '3000-metres-steeplechase', EVENTS.keys()), AGE_CATEGORY, BEST_RESULTS_ONLY, REGION_TYPE, GENDER, MAX_RESULTS_BY_COUNTRY):
    path = f'data/indoor/{event}/{gender}/{year}-{age_category}-{best_results_only}-{max_results_by_country}-{region_type}.csv'
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as results_file:
        writer = csv.writer(results_file)
        writer.writerow(HEADERS)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for page in PAGES:
                futures.append(executor.submit(get_top_list, event, 'indoor', gender, age_category, year, EVENTS[event], page=page, regionType=region_type, bestResultsOnly=best_results_only, ageCategory=age_category, maxResultsByCountry=max_results_by_country))
                        
            for future in futures:
                results = future.result()
                if results is not None:
                    writer.writerows(results)

for (year, event, age_category, best_results_only, region_type, gender, max_results_by_country) in itertools.product(YEARS, filter(lambda e: e != '60-metres' and e != '3000-metres', EVENTS.keys()), AGE_CATEGORY, BEST_RESULTS_ONLY, REGION_TYPE, GENDER, MAX_RESULTS_BY_COUNTRY):
    path = f'data/outdoor/{event}/{gender}/{year}-{age_category}-{best_results_only}-{max_results_by_country}-{region_type}.csv'
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as results_file:
        writer = csv.writer(results_file)
        writer.writerow(HEADERS)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for page in PAGES:
                futures.append(executor.submit(get_top_list, event, 'outdoor', gender, age_category, year, EVENTS[event], page=page, regionType=region_type, bestResultsOnly=best_results_only, ageCategory=age_category, maxResultsByCountry=max_results_by_country))
                        
            for future in futures:
                results = future.result()
                if results is not None:
                    writer.writerows(results)

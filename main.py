import requests
from bs4 import BeautifulSoup

import itertools
import csv
import os
from urllib.parse import urlencode

EVENTS = [
    '800-metres',
    '1000-metres',
    '1500-metres',
    'one-mile',
    '2000-metres',
    '3000-metres',
    'two-miles',
    '5000-metres',
    '10000-metres'
]

CURRENT_YEAR = 2023

YEARS = range(CURRENT_YEAR - 10, CURRENT_YEAR + 1)

NUM_PERFORMANCES = 1000

NUM_PAGES = int(NUM_PERFORMANCES / 100)

PAGES = range(1, NUM_PAGES + 1)

AGE_CATEGORY = ['senior'] # 'u18', 'u20'

BEST_RESULTS_ONLY = [False] # True

TRACK_SIZE = ['regular'] # 'irregular', 'all'

REGION_TYPE = ['world']

GENDER = ['men', 'women']

def get_top_list(event, environment, gender, age_category, year, event_category='middle-long', **kwargs):
    url = f'https://worldathletics.org/records/toplists/{event_category}/{event}/{environment}/{gender}/{age_category}/{year}?{urlencode(kwargs)}'

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

for (year, event, age_category, best_results_only, track_size, region_type, gender) in itertools.product(YEARS, filter(lambda e: e != '10000-metres', EVENTS), AGE_CATEGORY, BEST_RESULTS_ONLY, TRACK_SIZE, REGION_TYPE, GENDER):
    path = f'data/indoor/{event}/{gender}/{year}-{age_category}-{best_results_only}-{track_size}-{region_type}.csv'
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as results_file:
        writer = csv.writer(results_file)
        writer.writerow(HEADERS)
        for page in PAGES:
            results = get_top_list(event, 'indoor', gender, age_category, year, page=page, regionType=region_type, bestResultsOnly=best_results_only, oversizedTrack=track_size)
            if results is not None:
                writer.writerows(results)

for (year, event, age_category, best_results_only, region_type, gender) in itertools.product(YEARS, EVENTS, AGE_CATEGORY, BEST_RESULTS_ONLY, REGION_TYPE, GENDER):
    path = f'data/outdoor/{event}/{gender}/{year}-{age_category}-{best_results_only}-{region_type}.csv'
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as results_file:
        writer = csv.writer(results_file)
        writer.writerow(HEADERS)
        for page in PAGES:
            results = get_top_list(event, 'outdoor', gender, age_category, year, page=page, regionType=region_type, bestResultsOnly=best_results_only)
            if results is not None:
                writer.writerows(results)

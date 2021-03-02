import requests
from bs4 import BeautifulSoup
import pandas as pd


def create_prime_soup(year, page, headers, path):
    '''Creates the primal soup for a particular year.'''
    url = page + str(year)
    tree = requests.get(url, headers=headers)
    soup = BeautifulSoup(tree.content, 'html.parser')
    # store the page first
    with open(path + 'prime_page_' + str(year) +
              '.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    return print(f'prime_page ' + str(year) + " created")


def store_prime_soup(begin_year, end_year, page, headers, path):
    """ Store the primal soup for a range of years 
    ( begin year to end year inclusive)."""
    x = [i for i in range(begin_year, end_year+1)]
    for i in range(len(x)):
        create_prime_soup(x[i], page, headers, path)
    return print(f'prime pages all years from ' + str(begin_year) + ' to '
                 + str(end_year) + ' stored')


path = 'new_data/html/'
year = '2019'
page = 'https://www.transfermarkt.de/1-bundesliga/tabelle/wettbewerb/L1?saison_id='
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}

store_prime_soup(2010, 2020, page, headers, path)

import scrapelib
from bs4 import BeautifulSoup
import json

s = scrapelib.Scraper(requests_per_minute=60,
                      raise_errors=False,
                      retry_attempts=10)
s.cache_storage = scrapelib.cache.FileCache('cache')
s.cache_write_only = False

main_url = 'http://www.chicagoelections.com/en/election3.asp'

def selectOptions(resp) :
    soup = BeautifulSoup(resp.content)
    options = soup.find_all('select', attrs={'name' : 'D3'})
    if options :
        for option in options[0].find_all('option') :
            option_value = option.get('value')
            if option_value is not None :
                yield option_value

election_dictionary = {}
    
for election in selectOptions(s.get(main_url)) :
    payload = {'D3': election, 'B1': 'View', 'flag1' : 1}
    resp = s.post(main_url, data=payload)
    election_url = resp.url
    election_dictionary[election.strip()] = {}
    print(election.strip())
    for race in selectOptions(resp) :
        payload = {'D3' : race, 'flag' : 1, 'B1' : '  View the Results'}
        resp = s.post(election_url, data=payload)
        soup = BeautifulSoup(resp.content)
        precinct_pages = []
        for link in soup.findAll('a') :
            precinct_pages.append('http://www.chicagoelections.com/' 
                                  + link['href'])

        election_dictionary[election.strip()][race.strip()] = precinct_pages
        print(race.strip())

            
with open('precinct_pages.json', 'w') as outfile:
  json.dump(election_dictionary, 
            outfile, 
            sort_keys=True, 
            indent=4, 
            separators=(',', ': '))

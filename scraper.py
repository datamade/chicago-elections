import scrapelib
from BeautifulSoup import BeautifulSoup
import requests
import json

class PostCache(scrapelib.Scraper) :
    def key_for_request(self, method, url, **kwargs):
        if method == 'get':
            return requests.Request(url=url,
                                    params=kwargs.get('params', {})).prepare().url
        if method == 'post' :
            return requests.Request(url=url,
                                    params=kwargs.get('data', {})).prepare().url
            

s = PostCache(requests_per_minute=10,
              follow_robots=True)
s.cache_storage = scrapelib.cache.FileCache('cache')
s.cache_write_only = False

main_url = 'http://www.chicagoelections.com/election3.asp'

def selectOptions(resp) :
    soup = BeautifulSoup(resp)
    options = soup.findAll('select', attrs={'name' : 'D3'})
    if options :
        for option in options[0].findAll('option') :
            option_value = option.get('value')
            if option_value is not None :
                yield option_value

election_dictionary = {}
    
for election in selectOptions(s.urlopen(main_url)) :
    payload = {'D3': election, 'B1': 'View', 'flag1' : 1}
    resp = s.urlopen(main_url, 'POST', payload)
    election_url = resp.response.url
    election_dictionary[election.strip()] = {}
    print election.strip()
    for race in selectOptions(resp) :
        payload = {'D3' : race, 'flag' : 1, 'B1' : '  View the Results'}
        resp = s.urlopen(election_url, 'POST', payload)
        soup = BeautifulSoup(resp)
        precinct_pages = []
        for link in soup.findAll('a') :
            precinct_pages.append('http://www.chicagoelections.com' 
                                  + link['href'])

        election_dictionary[election.strip()][race.strip()] = precinct_pages
        print race.strip()

            
with open('precinct_pages.json', 'w') as outfile:
  json.dump(election_dictionary, 
            outfile, 
            sort_keys=True, 
            indent=4, 
            separators=(',', ': '))

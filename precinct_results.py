import scrapelib
from BeautifulSoup import BeautifulSoup
import json
import sqlite3
import re
from urlparse import urlparse, parse_qs

conn = sqlite3.connect('results.db', timeout=10)
c = conn.cursor()

#c.execute("DROP TABLE IF EXISTS election")
#c.execute("DROP TABLE IF EXISTS race")
#c.execute("DROP TABLE IF EXISTS result")

c.execute('''CREATE TABLE IF NOT EXISTS election
             (election_id integer PRIMARY KEY, name TEXT)
          ''')
c.execute('''CREATE TABLE IF NOT EXISTS race 
             (race_id integer PRIMARY KEY, election_id integer, name TEXT)
          ''')
c.execute('''CREATE TABLE IF NOT EXISTS result 
             (result_id integer PRIMARY KEY, 
              race_id integer, option TEXT, ward INTEGER, 
              precinct INTEGER, votes INTEGER)
          ''')

s = scrapelib.Scraper(requests_per_minute=60,
                      follow_robots=True,
                      raise_errors=False,
                      retry_attempts=0)
s.cache_storage = scrapelib.cache.FileCache('cache')
s.cache_write_only = False

with open('precinct_pages.json') as infile :
    precinct_pages = json.loads(infile.read())

def parseTable(results_table) :
    for row in results_table.findAll('tr'):
        row_list = []
        cells = row.findAll('td')
        if len(cells) < 2:
            continue
        for cell in cells:
            row_list.append(cell.text)
        if len(row_list) > 2:
            yield row_list[::2]
        else:
            yield row_list



for election, races in precinct_pages.items() :
    c.execute("SELECT election_id FROM election WHERE name = ?", 
              (election,))
    result = c.fetchone()
    if result :
        election_id = result[0]
    else :
        c.execute("INSERT INTO election (name) VALUES (?)", (election,))
        election_id = c.lastrowid
    for race, pages in races.items():
        c.execute("SELECT race_id from race WHERE name = ? AND election_id = ?", (race, election_id))
        race_id = c.fetchone()
        if race_id:
            race_id = race_id[0]
        else:
            c.execute("INSERT INTO race (election_id, name) VALUES (?, ?)", 
                      (election_id, race))
            race_id = c.lastrowid
        for page in pages :
            print page
            ward = parse_qs(urlparse(page).query)['Ward'][0]
            c.execute('select result_id from result where race_id = ? and ward = ?', (race_id, ward))
            result_rows = c.fetchone()
            if result_rows:
                continue
            soup = BeautifulSoup(s.urlopen(page))
            results_table = soup.find('table')
            table = parseTable(results_table) 
            try: 
                header = table.next()
                header = header[1:]
            except AttributeError :
                continue #logging


            for results in table :
                try :
                    precinct = results.pop(0)
                    int(precinct) # if we can't cast this to int then raise error
                    for result in zip(header, results):
                        c.execute("INSERT INTO result (race_id, ward, precinct, option, votes) VALUES (?, ?, ?, ?, ?)",
                                  [race_id] + [ward] + [precinct] + list(result))

                except ValueError, e:
                    print e
                    continue
            conn.commit()

conn.close()

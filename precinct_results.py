import scrapelib
from BeautifulSoup import BeautifulSoup
import json
import sqlite3
import re

conn = sqlite3.connect('results.db', timeout=10)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS election")
c.execute("DROP TABLE IF EXISTS race")
c.execute("DROP TABLE IF EXISTS result")

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

def parseTable(table) :
    for row in results_table.findAll('tr') :
        row_list = []
        for cell in row.findAll('td') :
            if cell.text == '--' :
                break
            row_list.append(cell.text)
        if row_list :
            yield row_list[::2]



for election, races in precinct_pages.items() :
    c.execute("SELECT election_id FROM election WHERE name = ?", 
              (election,))
    result = c.fetchone()
    if result :
        election_id = result[0]
    else :
        c.execute("INSERT INTO election (name) VALUES (?)", (election,))
        election_id = c.lastrowid
    for race, pages in races.items() :
        c.execute("INSERT INTO race (election_id, name) VALUES (?, ?)", 
                  (election_id, race))
        race_id = c.lastrowid
        for page in pages :
            print page
            ward = re.search('.*Ward=(.+?)&', page).group(1)
            print ward
            soup = BeautifulSoup(s.urlopen(page))
            results_table = soup.find('table')
            table = parseTable(results_table) 
            try: 
                header = table.next()[1:]
            except AttributeError :
                continue #logging


            for results in table :
                try :
                    precinct = results.pop(0)
                    int(precinct) # if we can't cast this to int then raise error
                    for result in zip(header, results) :
                        c.execute("INSERT INTO result (race_id, ward, precinct, option, votes) VALUES (?, ?, ?, ?, ?)",
                                  [race_id] + [ward] + [precinct] + list(result))
                except ValueError :
                    continue
            conn.commit()

conn.close()

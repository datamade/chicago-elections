import scrapelib
from BeautifulSoup import BeautifulSoup
import json
import sqlite3
import re
from urlparse import urlparse, parse_qs
import os
from app import db, Result, Election, BallotsCast, Voters
import csv
from datetime import date

s = scrapelib.Scraper(requests_per_minute=60,
                      follow_robots=True,
                      raise_errors=False,
                      retry_attempts=0)
s.cache_storage = scrapelib.cache.FileCache('cache')
s.cache_write_only = False

elex_dates = {}
with open('election_dates.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        year, month, day = row['Date'].split('-')
        elex_dates[row['Election']] = date(int(year), int(month), int(day))

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

def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance, True

def get_race_tables(pages):
    for page in pages:
        ward = parse_qs(urlparse(page).query)['Ward'][0]
        soup = BeautifulSoup(s.urlopen(page))
        results_table = soup.find('table')
        table = parseTable(results_table) 
        try: 
            header = table.next()
            header = header[1:]
            yield ward, header, table
        except AttributeError :
            continue #logging

def load_race(election, race_name, pages):
    ballots_cast = False
    voters = False
    data = {
        'race_name': race_name,
        'election_id': election.id
    }
    if 'ballots' in race_name.lower():
        ballots_cast = True
    if 'registered' in race_name.lower():
        voters = True
    for ward, header, table in get_race_tables(pages):
        for results in table:
            try :
                precinct = results.pop(0)
                int(precinct) # if we can't cast this to int then raise error
                data['ward'] = ward
                data['precinct'] = precinct
                if len(results) < 2:
                    if ballots_cast:
                        data['votes'] = results[0]
                        bc, created = get_or_create(BallotsCast, **data)
                        if created:
                            print 'Created: %s' % bc
                    elif voters:
                        data['count'] = results[0]
                        v, created = get_or_create(Voters, **data)
                        if created:
                            print 'Created: %s' % v
                    else:
                        if header[0] != 'No Candidate':
                            data['option'] = header[0]
                            data['votes'] = results[0]
                            r, created = get_or_create(Result, **data)
                            if created:
                                print 'Created %s' % r
                else:
                    for option,votes in zip(header, results):
                        data['option'] = option
                        data['votes'] = votes
                        r, created = get_or_create(Result, **data)
                        if created:
                            print 'Created %s' % r
            except ValueError, e:
                continue

def load_election(election, races):
    date = elex_dates[election]
    election, created = get_or_create(Election, name=election, date=date)
    for race_name, pages in races.items():
        load_race(election, race_name, pages)

if __name__ == '__main__':
    db.create_all()
    with open('precinct_pages.json') as infile :
        precinct_pages = json.loads(infile.read())
    for election, races in precinct_pages.items():
        load_election(election, races)

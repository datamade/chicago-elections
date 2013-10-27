import scrapelib
from BeautifulSoup import BeautifulSoup
import json
import re
from urlparse import urlparse, parse_qs
import os
from chicago_elections.models import Result, Election, BallotsCast, Voters
import csv
from datetime import date

from django.core.management import BaseCommand, CommandError, handle_default_options

DIR = os.path.dirname(os.path.abspath(__file__))
scraper = scrapelib.Scraper(requests_per_minute=60,
                  follow_robots=True,
                  raise_errors=False,
                  retry_attempts=0)
scraper.cache_storage = scrapelib.cache.FileCache(os.path.join(DIR, 'cache'))
scraper.cache_write_only = False

class Command(BaseCommand):
    args=''
    help=''
    option_list=BaseCommand.option_list + ()

    def get_version(self):
        return "0.1"


    def handle(self, *args, **kwargs):
        with open(os.path.join(DIR, 'precinct_pages.json'), 'rb') as infile :
            precinct_pages = json.loads(infile.read())

        elex_dates = {}
        with open(os.path.join(DIR, 'election_dates.csv'), 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                year, month, day = row['Date'].split('-')
                elex_dates[row['Election']] = date(int(year), int(month), int(day))
            for election, races in precinct_pages.items():
                elec_date = elex_dates[election]
                election, created = Election.objects.get_or_create(name=election, date=elec_date)
                for race_name, pages in races.items():
                    # Might want to fork here since the ballots cast and registered voters
                    # tables are not really races, per se. 
                    ballots_cast = False
                    voters = False
                    data = {
                        'race_name': race_name,
                        'election': election
                    }
                    if 'ballots' in race_name.lower():
                        ballots_cast = True
                    if 'registered' in race_name.lower():
                        voters = True
                    for ward, header, table in self.get_race_tables(pages):
                        for results in table:
                            try :
                                precinct = results.pop(0)
                                int(precinct) # if we can't cast this to int then raise error
                                data['ward'] = ward
                                data['precinct'] = precinct
                                if len(results) < 2:
                                    if ballots_cast:
                                        data['votes'] = results[0]
                                        bc, created = BallotsCast.objects.get_or_create(**data)
                                        if created:
                                            print 'Created: %s' % bc
                                    elif voters:
                                        data['count'] = results[0]
                                        v, created = Voters.objects.get_or_create(**data)
                                        if created:
                                            print 'Created: %s' % v
                                else:
                                    for option,votes in zip(header, results):
                                        data['option'] = option
                                        data['votes'] = votes
                                        r, created = Result.objects.get_or_create(**data)
                                        if created:
                                            print 'Created %s' % r
                            except ValueError, e:
                                continue

    def parseTable(self, results_table):
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
 
    def get_race_tables(self, pages):
        for page in pages:
            print page
            ward = parse_qs(urlparse(page).query)['Ward'][0]
            soup = BeautifulSoup(scraper.urlopen(page))
            results_table = soup.find('table')
            table = self.parseTable(results_table) 
            try: 
                header = table.next()
                header = header[1:]
                yield ward, header, table
            except AttributeError :
                continue #logging

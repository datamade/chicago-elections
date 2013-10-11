from app import db as new_db, Result, Race, Election
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import csv
from datetime import date

LOOKUP = {
    'result': Result,
    'race': Race,
    'election': Election
}
new_db.create_all()
old_engine = create_engine('sqlite:///results.db')
meta = MetaData()
meta.reflect(bind=old_engine)
Session = sessionmaker()
sess = Session(bind=old_engine)

def make_table(table_name, dates=None):
    table = meta.tables[table_name]
    colnames = [c.name for c in table.columns]
    for row in sess.query(table).all():
        data = {}
        for k,v in zip(colnames, row):
            data[k] = v
        if dates:
            data['date'] = dates[data['name']]
        new_table = LOOKUP[table_name]
        new_db.session.add(new_table(**data))
        try:
            new_db.session.commit()
        except IntegrityError:
            new_db.session.rollback()

if __name__ == "__main__":
    elex_dates = {}
    with open('election_dates.csv', 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year, month, day = row['Date'].split('-')
            elex_dates[row['Election']] = date(int(year), int(month), int(day))
    make_table('election', dates=elex_dates)
    make_table('race')
    make_table('result')
        



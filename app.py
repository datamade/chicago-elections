from flask import Flask, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import cast
from sqlalchemy import VARCHAR
from sqlalchemy import func
import json
from operator import attrgetter
from itertools import groupby
import os
from datetime import date

app = Flask(__name__)
CONN_STRING = os.environ['ELECTIONS_CONN']
app.config['SQLALCHEMY_DATABASE_URI'] = CONN_STRING

db = SQLAlchemy(app)

class Election(db.Model):
    __tablename__ = 'election'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    date = db.Column(db.Date, index=True)
    election_type = db.Column(db.String(255), index=True)
    ballots_cast = db.relationship('BallotsCast', backref='election', lazy='dynamic')
    voters = db.relationship('Voters', backref='election', lazy='dynamic')
    results = db.relationship('Result', backref='election', lazy='dynamic')

    def __repr__(self):
        return '<Election %r>' % self.name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class BallotsCast(db.Model):
    __tablename__ = 'ballots_cast'
    id = db.Column(db.Integer, primary_key=True)
    race_name = db.Column(db.String, index=True)
    ward = db.Column(db.Integer, index=True)
    precinct = db.Column(db.Integer, index=True)
    votes = db.Column(db.Integer)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), index=True)

    def __repr__(self):
        return '<BallotsCast Election: %s, Ward: %r, Precinct: %s>' % (self.election.name, self.ward, self.precinct)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Voters(db.Model):
    __tablename__ = 'voters'
    id = db.Column(db.Integer, primary_key=True)
    race_name = db.Column(db.String, index=True)
    ward = db.Column(db.Integer, index=True)
    precinct = db.Column(db.Integer, index=True)
    count = db.Column(db.Integer)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), index=True)

    def __repr__(self):
        return '<Voters Election: %s, Ward: %r, Precinct: %s>' % (self.election.name, self.ward, self.precinct)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    race_name = db.Column(db.String(255), index=True)
    option = db.Column(db.String(255), index=True)
    ward = db.Column(db.Integer, index=True)
    precinct = db.Column(db.Integer, index=True)
    votes = db.Column(db.Integer)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), index=True)
    
    def __repr__(self):
        return '<Result %r %r %r>' % (self.election.name, self.race_name, self.option)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

dthandler = lambda obj: obj.isoformat() if isinstance(obj, date) else None

def aggregate(election, relation, attr, agg_key, filters={}):
    objs = getattr(election, relation).filter_by(**filters).all()
    sorted_rel = sorted(objs, key=attrgetter(agg_key))
    group_by = []
    for k, g in groupby(sorted_rel, key=attrgetter(agg_key)):
        group_by.append({k:list(g)})
    relation_list = []
    for ballot in group_by:
        key = ballot.keys()[0]
        count = sum([getattr(b, attr) for b in ballot[key]])
        relation_list.append({agg_key: key, 'count': count})
    return relation_list

@app.route('/ballots/<int:election_id>/')
def ballots_by_id(election_id):
    election = Election.query.get(election_id)
    if not election:
        r = {
            'status': 'error',
            'message': 'No election with id "%s" found' % election_id
        }
        resp = make_response(json.dumps(r), 404)
    else:
        ballots = aggregate(election, 'ballots_cast', 'votes', 'ward')
        outp = {
            'election': election.as_dict(),
            'ballots_cast': ballots,
        }
        resp = make_response(json.dumps(outp, default=dthandler))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/elections/<int:election_id>/')
def elections_by_id(election_id):
    election = Election.query.get(election_id)
    ward_filter = request.args.get('ward')
    precinct_filter = request.args.get('precinct')
    if not election:
        r = {
            'status': 'error',
            'message': 'No election with id "%s" found' % election_id
        }
        resp = make_response(json.dumps(r), 404)
    else:
        filters = {}
        if ward_filter:
            filters['ward'] = ward_filter
        if precinct_filter:
            filters['precinct'] = precinct_filter
        ballots = aggregate(election, 'ballots_cast', 'votes', 'ward', filters=filters)
        voters = aggregate(election, 'voters', 'count', 'ward', filters=filters)
        # This query can take a while (5+ seconds) on the larger elections
        # Perhaps a better approach is needed. 
        query = db.session.query(Result.ward, Result.option, 
            Result.race_name, func.sum(Result.votes), 
            func.count(Result.precinct)) \
            .filter(Result.election_id == election.id) \
            .filter_by(**filters) \
            .group_by(Result.ward, Result.race_name, Result.option).all()
        db.session.close()
        header = ['ward', 'option', 'race', 'votes', 'precinct_count']
        results = []
        for r in query:
            res = {}
            for k,v in zip(header, r):
                res[k] = v
            results.append(res)
        outp = {
            'election': election.as_dict(),
            'ballots_cast': ballots,
            'voters': voters,
            'results': results
        }
        resp = make_response(json.dumps(outp, default=dthandler))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/elections/')
def elections():
    elections_avail = [{'name': e.name, 'id': e.id, 'date': e.date} for e in Election.query.order_by('date').all()]
    resp = make_response(json.dumps(elections_avail, default=dthandler))
    resp.headers['Content-Type'] = 'application/json'
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=9999)

# Return number of votes cast for a given option in a given race
# it = db.session.query(Result, func.sum(Result.votes)).filter(Result.race_id==race.race_id).group_by(Result.option)

# Return the number of votes cast in all races for options like "%MOORE%"
# it = db.session.query(Result, func.sum(Result.votes)).join(Race).filter(Result.option.like("%MOORE%")).group_by(Race)

# Total number of votes by ward in last democratic primary

# Added election type General, Primary, General special, Priamry Special

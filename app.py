from flask import Flask, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy
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

@app.route('/ballots/')
def ballots():
    election = request.args.get('election')
    if not election:
        resp = make_response('{"status": "error", "message": "You must provide the name of an election"}', 400)
    else:
        elex = Election.query.filter_by(name=election).first()
        if not elex:
            resp = make_response('{"status": "error", "message": "No election called \'%s\' found"}' % election, 404)
        else:
            by_ward = sorted(elex.ballots_cast.all(), key=attrgetter('ward'))
            groups_by_ward = []
            for k, g in groupby(by_ward, key=attrgetter('ward')):
                groups_by_ward.append({k:list(g)})
            ballots_by_ward = []
            for ballot in groups_by_ward:
                ward = ballot.keys()[0]
                count = sum([b.votes for b in ballot[ward]])
                ballots_by_ward.append({'ward':ward, 'count': count})
            outp = {'election': elex.as_dict(), 'ballots_cast': ballots_by_ward}
            dthandler = lambda obj: obj.isoformat() if isinstance(obj, date) else None
            resp = make_response(json.dumps(outp, default=dthandler))
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

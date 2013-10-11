from flask import Flask, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
import json
from operator import attrgetter
from itertools import groupby

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///election_results.db'

db = SQLAlchemy(app)

class Election(db.Model):
    election_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    date = db.Column(db.Date, index=True)
    races = db.relationship('Race', backref='election', lazy='dynamic')

    def __repr__(self):
        return '<Election %r>' % self.name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Race(db.Model):
    race_id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.election_id'), index=True)
    name = db.Column(db.String(255), index=True)
    results = db.relationship('Result', backref='race', lazy='dynamic')

    def __repr__(self):
        return '<Race %r>' % self.name 
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Result(db.Model):
    result_id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(255), index=True)
    ward = db.Column(db.Integer, index=True)
    precinct = db.Column(db.Integer, index=True)
    votes = db.Column(db.Integer)
    race_id = db.Column(db.Integer, db.ForeignKey('race.race_id'), index=True)
    
    def __repr__(self):
        return '<Result %r %r %r>' % (self.race.election.name, self.race.name, self.option)
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@app.route('/votes/')
def votes():
    # Total number of votes by ward in last democratic primary
    election = request.args.get('election')
    if not election:
        resp = make_response('{"status": "error", "message": "You must provide the name of an election"}', 400)
    else:
        elex = Election.query.filter_by(name=election).first()
        if not elex:
            resp = make_response('{"status": "error", "message": "No election called \'%s\' found"}' % election, 404)
        else:
            all_results = Result.query.join(Race).filter(Race.election_id == elex.election_id)
            all_results = sorted(all_results, key=attrgetter('ward'))
            groups_by_ward = []
            for k,g in groupby(all_results, key=attrgetter('ward')):
                groups_by_ward.append({k:list(g)})
            results_by_ward = []
            for result in groups_by_ward:
                ward = result.keys()[0]
                votes = sum([r.votes for r in result[ward]])
                results_by_ward.append({ward:votes})
            resp = make_response(json.dumps(results_by_ward))
    resp.headers['Content-Type'] = 'application/json'
    return resp

if __name__ == "__main__":
    app.run(debug=True)

# Return number of votes cast for a given option in a given race
# it = db.session.query(Result, func.sum(Result.votes)).filter(Result.race_id==race.race_id).group_by(Result.option)

# Return the number of votes cast in all races for options like "%MOORE%"
# it = db.session.query(Result, func.sum(Result.votes)).join(Race).filter(Result.option.like("%MOORE%")).group_by(Race)

# Total number of votes by ward in last democratic primary

# Added election type General, Primary, General special, Priamry Special

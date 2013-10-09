from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'

db = SQLAlchemy(app)

class Election(db.Model):
    election_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    races = db.relationship('Race', backref='election', lazy='dynamic')

    def __repr__(self):
        return '<Election %r>' % self.name 

class Race(db.Model):
    race_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    election_id = db.Column(db.Integer, db.ForeignKey('election.election_id'))
    results = db.relationship('Result', backref='race', lazy='dynamic')

    def __repr__(self):
        return '<Race %r>' % self.name 

class Result(db.Model):
    result_id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(255))
    ward = db.Column(db.Integer)
    precinct = db.Column(db.Integer)
    votes = db.Column(db.Integer)
    race_id = db.Column(db.Integer, db.ForeignKey('race.race_id'))
    
    def __repr__(self):
        return '<Result %r %r %r>' % (self.race.election.name, self.race.name, self.option)

# Return number of votes cast for a given option in a given race
# it = db.session.query(Result, func.sum(Result.votes)).filter(Result.race_id==race.race_id).group_by(Result.option)

# Return the number of votes cast in all races for options like "%MOORE%"
# it = db.session.query(Result, func.sum(Result.votes)).join(Race).filter(Result.option.like("%MOORE%")).group_by(Race)


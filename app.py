from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'

db = SQLAlchemy(app)

class Election(db.Model):
    election_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    
    def __repr__(self):
        return '<Election %r>' % self.name 

class Race(db.Model):
    race_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    election_id = db.Column(db.Integer, db.ForeignKey('election.election_id'))
    
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
        return '<Result %r>' % self.result_id



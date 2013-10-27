from mongoengine import *

class BallotsCast(Document):
    race_name = StringField()
    ward = IntField()
    precinct = IntField()
    votes = IntField()
    election = ReferenceField('Election')

    meta = {
        'indexes': ['race_name', 'ward', 'precinct']
    }

    def __repr__(self):
        return '<BallotsCast Ward: %r, Precinct: %s>' % (self.ward, self.precinct)
    
class Voters(Document):
    race_name = StringField()
    ward = IntField()
    precinct = IntField()
    count = IntField()
    election = ReferenceField('Election')

    meta = {
        'indexes': ['race_name', 'ward', 'precinct']
    }

    def __repr__(self):
        return '<Voters Ward: %r, Precinct: %s>' % (self.ward, self.precinct)
    
class Result(Document):
    race_name = StringField()
    option = StringField()
    ward = IntField()
    precinct = IntField()
    votes = IntField()
    election = ReferenceField('Election')
    
    meta = {
        'indexes': ['race_name', 'option', 'ward', 'precinct']
    }

    def __repr__(self):
        return '<Result %r %r>' % (self.race_name, self.option)

class Election(Document):
    election_id = IntField()
    name = StringField()
    date = DateTimeField()
    election_type = StringField()
    ballots_cast = ListField(ReferenceField(BallotsCast))
    voters = ListField(ReferenceField(Voters))
    results = ListField(ReferenceField(Result))
    
    meta = {
        'indexes': ['name', 'date', 'election_type',]
    }

    def __repr__(self):
        return '<Election %r>' % self.name



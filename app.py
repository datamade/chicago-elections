from flask import Flask, request, make_response
from flask.ext.cache import Cache
import pymongo
from bson import json_util
import json
from operator import itemgetter
from itertools import groupby
from datetime import date, datetime

app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

c = pymongo.MongoClient()
db = c['openelex']

dhandler = lambda obj: obj.isoformat() if isinstance(obj, date) or isinstance(obj, datetime) else None

@app.route('/elections/')
@cache.cached(timeout=60*60*24)
def elections():
    # Displays elections by ID and contests in each election
    contests = list(db['contest'].find())
    resp = []
    elections = sorted(contests, key=itemgetter('election_id'))
    for k,g in groupby(elections, key=itemgetter('election_id')):
        conts = [c['raw_office'] for c in list(g)]
        resp.append({k:conts})
    resp = make_response(json.dumps(resp, default=dhandler))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/elections/<election_id>/')
@cache.cached(timeout=60*60*24)
def elections_by_id(election_id):
    # Returns a single election and the results of the contests
    # in that election by ward
    resp = {'contests': [], 'registered_voters': 0, 'ballots_cast': 0}
    contests = list(db.contest.find({'election_id': election_id}))
    for contest in contests:
        d = {}
        pipeline = [{
            '$match': {
                'election_id': election_id, 
                'contest': contest['_id']
            }}, {
                '$group': {
                    '_id': '$candidate_slug', 
                    'votes': {
                        '$sum': '$total_votes'
                    },
                    'voters': {
                        '$sum': '$registered_voters'
                    },
                    'ballots_cast': {
                        '$sum': '$ballots_cast'
                    },
                    'cand_id': {
                        '$addToSet': '$candidate'
                    },
                    'juris': {
                        '$addToSet': '$raw_jurisdiction'
                    }
                }
            }
        ]
        results = db['result'].aggregate(pipeline)['result']
        city_wide = False
        if results:
            d['results'] = []
            votes = [r['votes'] for r in results]
            winning = max(votes)
            ballots = max([r['ballots_cast'] for r in results])
            d['election_id'] = election_id
            d['office'] = contest['office']['name']
            if 'Chicago, IL' in [r['juris'] for r in results]:
                city_wide = True
            for result in results:
                res = {}
                cand = db.candidate.find_one(result['cand_id'][0])
                res['votes'] = result['votes']
                d['registered_voters'] = result['voters']
                d['ballots_cast'] = result['ballots_cast']
                d['votes_cast'] = sum(votes)
                if res['votes'] == winning:
                    res['winner'] = True
                else:
                    res['winner'] = False
                res['name'] = cand['raw_full_name']
                percent = (float(res['votes']) / float(d['votes_cast'])) * 100
                res['percent'] = '%(percent).2f' % {'percent':percent}
                d['results'].append(res)
            if d:
                resp['contests'].append(d)
        if city_wide:
            resp['registered_voters'] = max([r['registered_voters'] for r in resp['contests']])
            resp['ballots_cast'] = max([r['ballots_cast'] for r in resp['contests']])
        else:
            resp['registered_voters'] = sum([r['registered_voters'] for r in resp['contests']])
            resp['ballots_cast'] = sum([r['ballots_cast'] for r in resp['contests']])
    resp = make_response(json_util.dumps(resp))
    resp.headers['Content-Type'] = 'application/json'
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=9999)

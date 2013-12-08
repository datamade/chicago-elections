from flask import Flask, request, make_response
import pymongo
from bson import json_util
import json
from operator import itemgetter
from itertools import groupby
from datetime import date, datetime

app = Flask(__name__)

c = pymongo.MongoClient()
db = c['openelex']

dhandler = lambda obj: obj.isoformat() if isinstance(obj, date) or isinstance(obj, datetime) else None

@app.route('/elections/')
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
def elections_by_id(election_id):
    # Returns a single election and the results of the contests
    # in that election by ward
    resp = []
    for ward in range(1,51):
        d = {}
        d['ward'] = ward
        pipeline = [{
            '$match': {
                'election_id': election_id, 
                'ocd_id': {
                    '$regex': r'ward:%s/precinct' % ward
                }
            }}, {
                '$group': {
                    '_id': '$candidate_slug', 
                    'votes': {
                        '$sum': '$total_votes'
                    },
                    'voters': {
                        '$sum': '$registered_voters'
                    },
                    'cand_id': {
                        '$addToSet': '$candidate'
                    },
                }
            }
        ]
        results = db['result'].aggregate(pipeline)['result']
        if results:
            d['results'] = []
            votes = [r['votes'] for r in results]
            d['votes_cast'] = sum(votes)
            winning = max(votes)
            d['election_id'] = election_id
            d['division'] = 'ocd-division/country:us/state:il/place:chicago'
            d['office_name'] = 'Alderman Ward %s' % ward
            for result in results:
                res = {}
                cand = db.candidate.find_one(result['cand_id'][0])
                res['votes'] = result['votes']
                res['voters'] = result['voters']
                if res['votes'] == winning:
                    res['winner'] = True
                else:
                    res['winner'] = False
                res['name'] = cand['raw_full_name']
                percent = (float(res['votes']) / float(d['votes_cast'])) * 100
                res['percent'] = '%(percent).2f' % {'percent':percent}
                d['results'].append(res)
        resp.append(d)
    resp = make_response(json_util.dumps(resp))
    resp.headers['Content-Type'] = 'application/json'
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=9999)

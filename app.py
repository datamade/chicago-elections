from flask import Flask, request, make_response
import pymongo
from bson import json_util
import json
from operator import itemgetter
from itertools import groupby

app = Flask(__name__)

c = pymongo.MongoClient()
db = c['openelex']

@app.route('/elections/')
def elections():
    # Returns all elections
    contests = list(db['contest'].find())
    resp = []
    for contest in contests:
        d = {
            'election_id': contest['election_id'],
            'office_name': contest['raw_office'],
            'division': 'ocd-division/country:us/state:il/place:chicago',
            'results': [],
        }
        print 'Contest: %s' % contest['raw_office']
      # for ward in range(1,51):
      #     d['ward'] = ward
      #     query = {
      #         'election_id': contest['election_id'],
      #         'ocd_id': {'$regex': r'ward:%s/precinct' % ward }
      #     }
      #     results = list(db['result'].find(query))
      #     results = sorted(results, key=itemgetter('candidate_slug'))
      #     print 'WARD: %s' % ward
      #     for k,g in groupby(results, key=itemgetter('candidate_slug')):
      #         print db['candidate'].find_one({'slug':k})['raw_full_name']
      # print '*'*100
        resp.append(d)
    resp = make_response(json_util.dumps(resp))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/elections/<election_id>/')
def elections_by_id(election_id):
    # Returns a single election
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

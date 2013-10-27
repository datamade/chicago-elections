from .models import Election, Result, Voters, BallotsCast
from django.http import HttpResponse
from bson import json_util
import json

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

def ballots_by_id(request, election_id):
    try:
        election = Election.objects.get(election_id=election_id)
    except Election.DoesNotExist:
        r = {
            'status': 'error',
            'message': 'No election with id "%s" found' % election_id
        }
        return HttpResponse(json.dumps(r), mimetype="application/json", status_code=404)
    ward_filter = request.GET.get('ward')
    precinct_filter = request.GET.get('precinct')
    return HttpResponse(election.to_json(), mimetype='application/json')

# @app.route('/ballots/<int:election_id>/')
# def ballots_by_id(election_id):
#     election = Election.query.get(election_id)
#     if not election:
#         r = {
#             'status': 'error',
#             'message': 'No election with id "%s" found' % election_id
#         }
#         resp = make_response(json.dumps(r), 404)
#     else:
#         ballots = aggregate(election, 'ballots_cast', 'votes', 'ward')
#         outp = {
#             'election': election.as_dict(),
#             'ballots_cast': ballots,
#         }
#         resp = make_response(json.dumps(outp, default=dthandler))
#     resp.headers['Content-Type'] = 'application/json'
#     return resp
# def elections_by_id(election_id):
#     election = Election.query.get(election_id)
#     ward_filter = request.args.get('ward')
#     precinct_filter = request.args.get('precinct')
#     if not election:
#         r = {
#             'status': 'error',
#             'message': 'No election with id "%s" found' % election_id
#         }
#         resp = make_response(json.dumps(r), 404)
#     else:
#         filters = {}
#         if ward_filter:
#             filters['ward'] = ward_filter
#         if precinct_filter:
#             filters['precinct'] = precinct_filter
#         ballots = aggregate(election, 'ballots_cast', 'votes', 'ward', filters=filters)
#         voters = aggregate(election, 'voters', 'count', 'ward', filters=filters)
#         # This query can take a while (5+ seconds) on the larger elections
#         # Perhaps a better approach is needed. 
#         query = db.session.query(Result.ward, Result.option, 
#             Result.race_name, func.sum(Result.votes), 
#             func.count(Result.precinct)) \
#             .filter(Result.election_id == election.id) \
#             .filter_by(**filters) \
#             .group_by(Result.ward, Result.race_name, Result.option).all()
#         db.session.close()
#         header = ['ward', 'option', 'race', 'votes', 'precinct_count']
#         results = []
#         for r in query:
#             res = {}
#             for k,v in zip(header, r):
#                 res[k] = v
#             results.append(res)
#         outp = {
#             'election': election.as_dict(),
#             'ballots_cast': ballots,
#             'voters': voters,
#             'results': results
#         }
#         resp = make_response(json.dumps(outp, default=dthandler))
#     resp.headers['Content-Type'] = 'application/json'
#     return resp
#
# def elections():
#     elections_avail = [{'name': e.name, 'id': e.id, 'date': e.date} for e in Election.query.order_by('date').all()]
#     resp = make_response(json.dumps(elections_avail, default=dthandler))
#     resp.headers['Content-Type'] = 'application/json'
#     return resp
#
# def war_chest():
#     resp = make_response(open('war-chest.json').read())
#     resp.headers['Content-Type'] = 'application/json'
#     return resp
#
# def clout():
#     resp = make_response(open('clout.json').read())
#     resp.headers['Content-Type'] = 'application/json'
#     return resp
#
# def aldermen():
#     resp = make_response(open('aldermen.json').read())
#     resp.headers['Content-Type'] = 'application/json'
#     return resp


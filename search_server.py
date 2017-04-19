"""
Testing for now, allows the clustering and searching algorithms to be accessed.
"""
import json
from bottle import run, post, request, response
import search


@post('/search')
def my_search():
    req_obj = json.loads(request.body.read())
    result = searching.search(req_obj['terms'])
    return str(result)


@post('/cluster')
def my_clustering():
    req_obj = json.loads(request.body.read())
    similar = cluster.find_similar_bills(req_obj['cluster'])
    return str(similar)

if __name__ == '__main__':
    cluster = search.ClusterFinder()
    searching = search.TermSearch()
    run(host='localhost', port=8080, debug=True)
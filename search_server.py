"""
Testing for now, allows the clustering and searching algorithms to be accessed.
"""
import json
from bottle import run, post, request, response, get
import configs
import search


@get('/search')
def my_search():
    req_obj = request.query['term']
    result = configs.searching.search(req_obj)
    return result


@get('/cluster')
def my_clustering():
    req_obj = request.query['cluster']
    similar = configs.cluster.find_similar_bills(req_obj)
    return similar

def run_server():
    run(host='localhost', port=8080, debug=True)


if __name__ == '__main__':
    run_server()


"""
MORE STUFF:
The search will give info about the bill:
{
   Name:...
   ID:...
}

for bills (the bill page): /bill/:id
{ Name:...
  Description:...
  Link:...
  Vote_info:
  Comments:
}

for the cluster: /cluster/:id
{
    same object as the search
}
"""
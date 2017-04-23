"""
Testing for now, allows the clustering and searching algorithms to be accessed.
"""
import json
from bottle import run, get
from bill_data_analysis import make_name
from collections import OrderedDict
import configs
import re


def sort_search(results):
    new_matrix = {}
    for page, r_dict in results.items():
        r_sorted = OrderedDict(sorted(r_dict.items(), key=lambda t: t[1]))
        new_matrix[page] = r_sorted
    return new_matrix

def get_year_bill(name):
    s_year = re.search('[0-9]{4}', name).group(0)
    s_bill = re.search('[A-Z]{2,}[0-9]{3,4}', name).group(0)
    return s_year, s_bill


@get('/engine/search/<term>')
def my_search(term):
    result = configs.searching.search(term)
    results = {}
    for page, tf_idf in result.items():
        name = make_name(page)
        year, bill = get_year_bill(name)
        results[year + bill] = configs.bill_info.get_summary(year, bill)
        results[year + bill]['tf_idf'] = tf_idf[0]
    #print(sort_search(results))
    return results


@get('/engine/cluster/<year>/<bill>')
def my_clustering(year, bill):
    bill_path = "{year}{bill}".format(year=year, bill=bill)
    similar = configs.cluster.find_similar_bills(bill_path)
    similar_bills = {'similar': []}
    for s in similar:
        s_year, s_bill = get_year_bill(s)
        similar_bills['similar'].append(configs.bill_info.get_summary(s_year, s_bill))
    return similar_bills


@get('/engine/bill_info/<year>/<bill>')
def bill_info(year, bill):
    return configs.bill_info.get_summary(year, bill)


@get('/engine/list/<year>')
def list_bills(year):
    bill_list = configs.bill_info.get_all_bills(str(year))
    return bill_list


def run_server():
    run(host='localhost', port=8081, debug=True)


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
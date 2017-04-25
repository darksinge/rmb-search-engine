"""
Testing for now, allows the clustering and searching algorithms to be accessed.
"""
from bottle import run, get
from get_bill_info import make_name
from offline_bill_scrape import needs_updates
from collections import OrderedDict
import configs
import re


def sort_search(results):
    """
    Sorts the dictionary of results returned from search. However, the ordered dictionary is not actually sent over the
    server, so unless we find another method to sort the object, this is useless.

    Parameters:
        results: dictionary, must be formatted according to the object returned by TermSearch.search(), otherwise it
         will crash

    Returns:
         OrderedDict: a dictionary that is ordered according to tf_idf score
    """
    r_dict = OrderedDict(sorted(results.items(), key=lambda t: t[1]['tf_idf'], reverse=True))
    return r_dict


def get_year_bill(name):
    """
    Takes the name of a bill and extracts the year and bill id

    Parameters:
        name: string, must already have the year and the bill id inside the string.

    Returns:
         string: the year the bill was written
         string: the id of the bill
    """
    s_year = re.search('[0-9]{4}', name).group(0)
    s_bill = re.search('[A-Z]{2,}[0-9]{3,4}', name).group(0)
    return s_year, s_bill


@get('/engine/search/<term>')
def my_search(term):
    """
    Takes a term from the server and returns a json object full of the results. Right now it is unsorted because
    Bottle cannot send an OrderedDict collection

    Parameters:
        term:

    Returns:

    """
    result = configs.searching.search(term)
    results = {}
    for page, tf_idf in result.items():
        name = make_name(page)
        year, bill = get_year_bill(name)
        results[year + bill] = configs.bill_info.get_summary(year, bill)
        results[year + bill]['tf_idf'] = tf_idf[0]
    return results


@get('/engine/cluster/<year>/<bill>')
def my_clustering(year, bill):
    """
    Finds and returns bills that are similar to a bill. Used on the server.

    Parameters:
        year: int/str, the year that the bill is from
        bill: str, name of the bill

    Returns:
         json.loads: a json object that can be used for the website with similar bills listed
    """
    bill_path = "{year}{bill}".format(year=year, bill=bill)
    similar = configs.cluster.find_similar_bills(bill_path)
    similar_bills = {'similar': []}
    for s in similar:
        s_year, s_bill = get_year_bill(s)
        similar_bills['similar'].append(configs.bill_info.get_summary(s_year, s_bill))
    return similar_bills


@get('/engine/bill_info/<year>/<bill>')
def bill_info(year, bill):
    """
    Gets information needed for the bill. Will also be used to get main content for the bill as well.

    Parameters:
        year: int/str, year the bill is from
        bill: str, id/name of the bill.

    Returns:
        json.dumps: json object with information about the bill in question
    """
    return configs.bill_info.get_summary(year, bill)


@get('/engine/list/<year>')
def list_bills(year):
    """
    Returns a list of all the bills passed in a year.

    Parameters:
        year:

    Returns:
         json.dumps: json object with all the bills from a year.
    """
    bill_list = configs.bill_info.get_all_bills(str(year))
    return bill_list


def run_server():
    if 'all' in needs_updates('2017'):
        from offline_bill_scrape import extract_files
        extract_files()
    else:
        # Note: if this is expanded beyond 2017, make sure this does something useful.
        print("No changes being made")
    run(host='localhost', port=8081, debug=True)


if __name__ == '__main__':
    run_server()
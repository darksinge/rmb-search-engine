import search
import get_bill_info
import os


def get_path():
    """
    Function to determine which path to use depending on environment.

    :return:
    """
    try:
        env = os.environ['PYTHON_ENV']
    except KeyError:
        env = 'development'

    if env == 'production':
        return os.path.join('var', 'www', 'rmb-search-engine')

    else:
        return ""

default_path = get_path()
cluster = search.ClusterFinder()
searching = search.TermSearch()
bill_info = get_bill_info.BillInfo()

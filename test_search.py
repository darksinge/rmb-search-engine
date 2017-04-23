"""
Client to communicate with search_server.py for testing/demonstration purposes. Good news it works
"""
import http.client


def help_me():
    """
    Just makes it like a regular console application, says that commands that can be used

    Returns:
         None
    """
    print("search: search for terms")
    print("cluster: search for similar documents")
    print("exit(): exits program")


def search():
    """
    Asks user for input and searches for the requested documents. User input can be anything (just about, obviously
    escape character would cause problems)

    Returns:
         None
    """
    terms = input("search: ")
    c = http.client.HTTPConnection('localhost', 8080)
    c.request('POST', '/search', '{"terms": ' + '"' + terms + '"}')
    doc = c.getresponse().read()
    print(doc)
    c.close()


def cluster():
    """
    Finds similar clusters to whatever the user inputs.

    Example inputs:

    'bill_files\\filtered\\2006\\HB0351'
    'bill_files\\filtered\\2004\\HB0262'
    'bill_files\\filtered\\1998\\HB0119'
    'bill_files\\filtered\\2016\\HJR022'

    Returns:
        None
    """
    document = input("document: ")
    c = http.client.HTTPConnection('localhost', 8080)
    c.request('POST', '/cluster', '{"cluster": ' + '"' + document + '"}')
    doc = c.getresponse().read()
    print(doc)


def main():
    user_input = ""
    while user_input != 'exit()':
        user_input = input(">>>")
        if user_input == 'help':
            help_me()
        elif user_input == 'search':
            search()
        elif user_input == cluster():
            cluster()
    pass


def search_sort():
    import search_server
    results = search_server.my_search("taxes")
    print(results)
    results_sorted = search_server.sort_search(results)
    print(results_sorted)

if __name__ == '__main__':
    search_sort()
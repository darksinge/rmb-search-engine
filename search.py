# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 08:32:10 2017

@author: Bradley Robinson

Code to search documents using csv, in the future it will use a SQL server
so a similar algorithm can be called in javascript

"""
import pandas as pd
import pickle
import os
import re

# TODO: http server,
class ClusterFinder(object):
    """

    """
    def __init__(self):
        self.clusters = pd.read_csv(os.path.join('analysis', 'clusters', 'with_max_clusters.csv'))
        cols = self.clusters.columns
        self.clusters.rename(columns={cols[0]: 'docs'}, inplace=True)
        self.clusters.set_index('docs', inplace=True)

    def find_similar_bills(self, bill_file_name):
        """
        Takes the name and location of a bill file, searches for it and returns five other bills that are similar based
        on K-Means clusters

        Parameters:
            bill_file_name: a string with the relative location of the bill file

        Returns:
            numpy string array: has five of the closest bills within the same cluster
        """
        try:
            found_doc = self.clusters.loc[bill_file_name]
            cluster_name = found_doc['cluster']
            docs_in_cluster = self.clusters[self.clusters['cluster'] == cluster_name]
            distances = abs((found_doc['X'] + found_doc['y']) - (docs_in_cluster['X'] + docs_in_cluster['y']))
            distances.sort_values(inplace=True)
            return distances.head(6).index[1:]
        except KeyError:
            return "Invalid document."

    def get_names(self, n):
        """
        Simply gets some file names to test the search with.

        Parameters:
            n: integer for how many file names needed

        Returns:
             list of file names of size n
        """
        files = self.clusters.sample(n).index
        return files.values


class TermSearch(object):

    def __init__(self):
        from collections import OrderedDict
        self.sparse_matrix = pickle.load(open(os.path.join('analysis', 'sparse_p.pickle'), 'rb'))

    def tokenize(self, text):
        stripped_text = re.sub('[^a-z0-9 *]', ' ', text.lower())
        terms = stripped_text.split()
        return terms

    def _search_term(self, term):
        try:
            doc_dict = self.sparse_matrix[term]
            return doc_dict
        except KeyError:
            return {}

    def combine_dicts(self, dict1, dict2):
        combined = dict2.copy()
        for k, terms in dict2.items():
            if k in dict1:
                combined[k] += dict1[k]
            else:
                combined[k] = dict1[k]
        return combined

    def search(self, text):
        terms = self.tokenize(text)
        current_dict = {}
        for i in range(len(terms)):
            docs = self._search_term(terms[i])
            if i > 0:
                current_dict = self.combine_dicts(current_dict, docs)
        # TODO: Order things
        return current_dict



def check_for_terms(tokens, df_columns):
    """
    Finds any terms that may be in the the dataframe. Should be called before
    creating a tf-idf with any hits for the search terms.
    
    Args:
        tokens - a Python list of tokenized terms to be searched for
        df_columns - a list of columns (or terms) in the document database
    Returns:
        A list of all the terms that have hits
    """
    pass


def csv_search(tokens, df):
    """
    Finds any hits in the CSV document. Note that in the future sql_search will
    be used for this, which will be optimized for the large matrix
    
    How it will be done:
        looks for each term in the columns
        if there are none, return failure
        Using the list for each hit, then create dataframes using OR operation
        for any that have tf-idf > 0
        
        Find new scores
        Order the documents
        Return ordered list
        
    Args:
        tokens: a Python list of tokenized terms to be searched for
        
    Returns:
        A tf_idf ordered list for any hits
    """
    searchable_terms = check_for_terms(tokens, df)
    if len(searchable_terms) == 0:
        # TODO: exception
        return None
    
    term_df = pd.DataFrame(columns=searchable_terms)
    for term in searchable_terms:
        with_term = df[df[term] > 0]
        # term_df.append()
        

def tokenize(unfiltered_text):
    """
    Takes search text and removes any extra figures, etc., to allow for a 
    search of the documents.
    """
    # TODO: Actually tokenize
    return unfiltered_text
    

def find_text(text, search_type="csv", df=None):
    """
    Retrieves tf-idf ordered results in a list for document search.
    bill_data_analysis.main() must be run if additional bill scraping has been
    done to ensure new bills are included in the search.
    
    Args:
        text: a string of search terms
        search_type: a string representing how the search will be done. 
        Accepted parameters are "csv" and "sql"
        df - If search_type="csv", this parameter must include a tf-idf table
        
    Returns:
        A tf-idf ordered list for any hits.
    """
    tokens = tokenize(text)
    if search_type == "csv":
        csv_search(tokens, df)
    else:
        # TODO: Throw exception
        pass
    return []


def test_search():
    """
    Used for development
    """
    dense_matrix = pd.read_csv(os.path.join("analysis", "dense_matrix.csv"))
    find_text(["bill", "rights", "taxes"], df=dense_matrix)


def open_files(lst, similar):
    """
    Takes a list of files and prints a few of the lines from them to check and make sure the algorithm worked
    :param lst:
    :return:
    """

    for f in lst:
        file = open(f + '.txt', 'r')
        contents = file.read()
        filtered_contents = re.sub('\\s', ' ', contents)
        print("------------------------------------------------------------------------------")
        print('Document: ', f, "\nSimilar to: ", similar)
        print("------------------------------------------------------------------------------")
        print(filtered_contents)
        print("------------------------------------------------------------------------------")

    
if __name__ == '__main__':
    """
    Implementation of a test of the main algorithm for our web site, K-Means clustering and distancing. Creates a
    ClusterFinder class, and uses cluster.get_names, which is a convenient little tool for testing. That just returns
    random file names so we can search for things similar to them.

    Using these random samples, we call ClusterFinder.find_similar_bills, which a) finds the cluster, b) orders the
    cluster by distance from the current file, and c) returns the top five matches.
    """
    cluster = ClusterFinder()
    results = {}
    for file in cluster.get_names(10):
        print("------------------------------------------------------------------------------")
        print("Files similar to {}".format(file))
        print("------------------------------------------------------------------------------")
        similar_clusters = cluster.find_similar_bills(file)
        results[file] = similar_clusters
        for c in similar_clusters:
            print(c)
        print('')
    search = TermSearch()
    import time
    time0 = time.time()
    a = search.search("taxes automobile")
    print("Search 2 terms in: {}".format(time.time() - time0))
    time0 = time.time()
    a = search.search("children housing authorities")
    print("Search 3 terms in: {}".format(time.time() - time0))
    time0 = time.time()
    a = search.search("tax time authority legislation excessive potter harry")
    print("Search 7 terms in: {}".format(time.time() - time0))
    """
    # To look at the actual files, it is possible to print them in the console using this call, but it is right now
    # easier to check the files individually in the /raw/ folder since the filtered versions are so messy. So far the
    # clustering has been somewhat meaningful with manual checks.
    for key, files in results.items():
        open_files(files, key)
    """
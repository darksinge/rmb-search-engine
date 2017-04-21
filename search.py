# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 08:32:10 2017

@author: Bradley Robinson

Searching algorithms for documents, along with some testing script to demonstrate the effectiveness of the algorithms.

"""
import pandas as pd
import pickle
import os
import re



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
    """
    Object created and used for search algorithm, this allows a term search to occur without loading the search contents
    into memory every time a search is done, which could be time consuming.

    Methods:
        tokenize:
        _search_term: internal method to find sparse_matrix terms


    Variables:
        self.sparse_matrix: a pre-loaded sparse_matrix for searching that allows users to search for terms. The document
        is a pickle that is created previously in create_sparse_matrix.py.
    """
    def __init__(self):
        # May be needed, for now we won't bother
        from collections import OrderedDict
        self.sparse_matrix = None
        self.refresh_matrix()

    def refresh_matrix(self):
        """
        If the matrix has been
        :return:
        """
        self.sparse_matrix = pickle.load(open(os.path.join('analysis', 'sparse_p.pickle'), 'rb'))

    def tokenize(self, text):
        """
        Strips non-numerical/alphabetical characters and splits up terms in the search.

        Parameters:
            text: string, search text to be tokenized

        Returns:
            list: strings of terms to be searched for
        """
        stripped_text = re.sub('[^a-z0-9 *]', ' ', text.lower())
        terms = stripped_text.split()
        return terms

    def _search_term(self, term):
        """
        Internal method to find the given term in the dictionary and return results, if there are any.

        Parameters:
            term: a single string that is just one term.

        Returns:
            dict: a dictionary with the matching results
        """
        try:
            doc_dict = self.sparse_matrix[term]
            return doc_dict
        except KeyError:
            return {}

    def combine_dicts(self, dict1, dict2):
        """
        Takes two dictionaries and combines them so that none of the documents are overridden. If two match between
        documents, they are added together.

        Parameters:
            dict1: dictionary of documents for the first term with document as key and the tf_idf score as the value
            dict2: same, but for the second term.

        Returns:
             dict: a dictionary with terms from both documents combined
        """
        combined = dict2.copy()
        for k, terms in dict2.items():
            if k in dict1:
                combined[k] += dict1[k]
        return combined

    def search(self, text):
        """
        Method to search for documents that match the users needs.

        Parameters:
            text: a string of text with terms representing a user's interest.
        Returns:
            dict: dictionary with documents and their tf_idf score.
        """
        terms = self.tokenize(text)
        current_dict = {}
        for i in range(len(terms)):
            docs = self._search_term(terms[i])
            if i > 0:
                current_dict = self.combine_dicts(current_dict, docs)
            else:
                current_dict = docs
        # TODO: Order things
        return current_dict


def scan_similar_documents(lst, similar):
    """
    Takes a list of files and prints a few of the lines from them to check and make sure the algorithm worked. Simply
    used for validation of the ClusterFinder algorithms.

    Parameters:
        lst: list or similar iterable of strings, goes through each file and prints the contents
        similar: string, name of the document that the listed documents represent

    Returns:
        None
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
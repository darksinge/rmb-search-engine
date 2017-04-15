# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 08:32:10 2017

@author: Bradley Robinson

Code to search documents using csv, in the future it will use a SQL server
so a similar algorithm can be called in javascript
"""
import pandas as pd
import os


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
    
    
    
    

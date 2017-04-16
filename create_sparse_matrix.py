"""
Creates a sparse inverse dictionary for tf-idf searches. The CSV file produced by bill_data_analysis.py is so large
that this file is needed to produce something much smaller to be used for the searches
"""
import pandas as pd
import os
import json


def small_matrix():
    """
    Creates a small matrix to test make_matrix() with. That way reading in the csv doesn't take a long time. It saves
    the file in analysis/ as tiny_matrix.csv. To test make_matrix, change the csv it reads to tiny_matrix.csv.

    Parameters:
        None

    Returns:
         None
    """
    dense_matrix = pd.read_csv(os.path.join("analysis", "dense_matrix.csv"))
    tiny_matrix = dense_matrix.iloc[0:100,:]
    tiny_matrix.to_csv(os.path.join("analysis", "tiny_matrix.csv"), index=False)


def make_matrix(matrix_file=None):
    """
    Takes an already saved dense matrix (csv format) and creates a dictionary with each word as a key and a dictionary
    of docs and tf_idf values as the value.

    Parameters:
        matrix_file: a path string for a csv dense matrix file. The first column must include the name of the documents
        and the rest be for terms, otherwise an error will be thrown.

    Returns:
        dictionary: A sparse matrix dictionary for each term in the dense matrix.

    """

    if matrix_file:
        dense_matrix = pd.read_csv(matrix_file)
    else:
        dense_matrix = pd.read_csv(os.path.join("analysis", "dense_matrix.csv"))

    terms = dense_matrix.columns
    dense_matrix = dense_matrix.rename(columns = {terms[0]: "doc"})
    sparse_matrix = {}

    for term in terms[1:]:
        doc_matches = dense_matrix[dense_matrix[term] > 0]
        just_docs_and_values = doc_matches[["doc", term]]
        just_docs_and_values.set_index("doc", inplace=True)
        just_docs_and_values.reset_index()
        transposed = just_docs_and_values.transpose()
        doc_dictionary = transposed.to_dict("list")
        if len(doc_dictionary) > 0:
            sparse_matrix[term] = doc_dictionary

    return sparse_matrix


def make_matrix_json(matrix_file=None):
    """
    Takes the file name of a csv for the dense matrix, and creates and saves a json with a sparse matrix.

    Parameters:
        matrix_file: a path string for a csv dense matrix file. The first column must include the name of the documents
        and the rest be for terms, otherwise an error will be thrown.

    Returns:
        None
    """
    full_matrix = make_matrix(matrix_file)
    matrix_json = json.dumps(full_matrix)
    file = open(os.path.join("analysis", "sparse.json"), 'w')
    file.write(matrix_json)
    file.close()

if __name__ == '__main__':
    make_matrix_json()


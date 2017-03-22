from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans, MiniBatchKMeans
import os
import glob
#import multiprocessing as mp

import pandas as pd
#import numpy as np
from time import time
import matplotlib.pyplot as plt
import random


# Reads through a set directory -/bill_files/filtered/ finding all txt files
# and adds them to a series.
def get_series():
    data_files = glob.glob(os.path.join('bill_files', 'filtered', '*.txt'))
    bill_dict = {}
    time1 = time()
    for d in data_files:
        text = open(d)
        doc_name = d.split('.txt')[0]
        bill_dict[doc_name] = text.read()
        text.close()
    bill_series = pd.Series(bill_dict)
    print('Raw data read in {}s'.format(time() - time1))
    return bill_series


# Receives a series of documents
# Returns a Tfidf vector
def vectorize(bill_series, save_vector=False):
    time1 = time()
    vectorizer = TfidfVectorizer(max_df=.4, min_df=2, stop_words='english')
    X = vectorizer.fit_transform(bill_series)
    if save_vector:
        if not os.path.exists('analysis'):
            os.mkdir('analysis')
        df = pd.DataFrame(X.todense(), index=bill_series.index, columns = vectorizer.get_feature_names())
        df.to_csv(os.path.join('analysis', 'dense_matrix.csv'))
    print('Vectorization done in {}s'.format(time() - time1))
    return X


# This is one way to create a vector for the words, but the tests reveal it performs incredibly poorly as 
# binary values. Has not been tested otherwise. Remains for testing purposes
def hashing_vector(bill_series):
    time1 = time()
    vectorizer = HashingVectorizer(binary=True)
    X = vectorizer.fit_transform(bill_series)
    print('Vectorization done in {}s'.format(time() - time1))
    return X


# Reduces dimensions using TruncatedSVD. So far this creates the best parameters
# for clustering, recommended to use prior to clustering
def dimensionality_reduction(X, components):
    t0 = time()
    svd = TruncatedSVD(components)
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)
    
    X = lsa.fit_transform(X)
    
    print('Dimensionality reduction done in {}s'.format(time() - t0))
    print('Explained variance of the SVD step: {}'.format(svd.explained_variance_ratio_.sum()))
    return X


# Uses MiniBatchKMeans by default, which is a faster implementation of KMeans 
# clustering that performs slightly lower than the regular implementation of KMeans
# only use param slow=True if the vector has been reduced using dimensionality_reduction
# Otherwise the analysis is exceptionally long (minutes) and the score does not significantly
# increase
def clustering(X, clusters=4, max_iter=100, slow=False, init_size=2000, batch_size=2000):
    time1 = time()
    
    if slow:
        km = KMeans(n_clusters=clusters, max_iter=max_iter)
    else:
        km = MiniBatchKMeans(n_clusters=clusters, max_iter=max_iter, init_size=init_size, batch_size=batch_size)
    clustered_distances = km.fit_transform(X)
    cluster_labels = km.labels_
    print('KMeans clustering done in {}s'.format(time() - time1))
    return clustered_distances, cluster_labels


# Uses the metric silhouette average to determine how well the documents have 
# clustered. The metric can go from -1 (really bad) to 1. The closer to 1 the better.
# Compares how similar an object is to its cluster (cohesion) compared to other clusters (separation)
def evaluate_cluster(X, labels):
    silhouette_avg =  silhouette_score(X, labels)
    return silhouette_avg


# Creates a scatter plot with the transformed distances of clustering
def make_cluster_fig(distances, labels, clusters):
    time1 = time()
    fig, ax = plt.subplots()
    ax.scatter(x=distances[:, 0], y = distances[:, 1],c=labels)
    ax.set_title("Transformed Visualization of Document KMeans with {} Clusters".format(clusters))
    plt.savefig(os.path.join('visualizations','kmeans_{}k.png'.format(clusters)))
    plt.close()
    print("Visualization done in {}s".format(time() - time1))


# Saves the clusters to a csv for future use.
def save_clusters(doc_names, labels, distances, num_clusters):
    time0 = time()
    df = pd.DataFrame({'cluster': labels, 'X': distances[:, 0], 'y': distances[:, 1]}, index=doc_names)
    if not os.path.exists(os.path.join('analysis', 'clusters')):
        os.mkdir(os.path.join('analysis', 'clusters'))
    df.sort_values('cluster', inplace=True)
    df.to_csv(os.path.join('analysis', 'clusters', 'with_{}_clusters.csv'.format(num_clusters)))
    print("Cluster csv saved in {}s".format(time() - time0))
    

# Returns number of words in a document
# NOTE: May be affected by extra spaces and tabs
def get_doc_lengths(bill):
    data = bill.split(' ')
    return len(data)


# Creates a histogram and saves a png to file in path -/visualizations
def hist(values, title, file_name):
    fix, ax = plt.subplots()
    ax.hist(values, bins=20)
    ax.set_title(title)
    ax.set_ylabel("Frequency")
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


# Creates a bar_graph and saves a png
def bar_graph(values, title, file_name):
    fig, ax = plt.subplots()
    ax.bar([.25 + x for x in range(len(values))], values)
    ax.set_title(title)
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


# Function creates a box plot and saves it to a file in path -/visualizations/
def box_plot(values, title, file_name):
    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_title(title)
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


# This is slow, only for testing purposes
# Used to test different parameters with a fixed k
def cluster_tests(X, k):
    scores_by_init = {}
    
    print('-------------------init_size-------------')
    for i in range(500, 10000, 100):
        distances, labels = clustering(X, k, init_size=i)
        avg_score = evaluate_cluster(X, labels)
        print("Score: ", avg_score, 'Size: ', i)
        scores_by_init[i] = avg_score

    print('-------------------batch-----------------')
    scores_by_batch = {}
    for i in range(500, 10000, 100):
        distances, labels = clustering(X, k, init_size=2700, batch_size=i)
        avg_score = evaluate_cluster(X, labels)
        print("Score: ", avg_score, 'Batch: ', i)
        scores_by_batch[i] = avg_score

    for i in range(500, 10000, 100):
        distances, labels = clustering(X, k, init_size=i, batch_size=i)
        avg_score = evaluate_cluster(X, labels)
        print("Score: ", avg_score, 'Batch: ', i)


# Was used for a multi-threading process, but so far is not usable
# Don't use unless you fix that other stuff.
def k_means_process(X, k, init_size, batch_size):
    distances, labels = clustering(X, k, init_size, batch_size)
    avg_score = evaluate_cluster(X, labels)
    if avg_score > .2:
        make_cluster_fig(distances, labels, k)
    return (k, avg_score, init_size, batch_size)
    #output.put()
    

# Creates a list with variables for to send to k_means_process
# Purpose: Experiment with parameters
def create_rand_variables(size):
    lst = []
    for i in range(size):
        k = random.randint(3,300)
        init_size = random.randint(100, 10000)
        batch_size = random.randint(100, 10000)
        lst.append((k, init_size, batch_size))
    return lst


# WARNING: DON'T RUN THIS UNLESS YOU ARE READY TO WAIT A WHILE, IT IS LONG AND
# DEMANDING OF SYSTEM RESOURCES. ALSO MAKE SURE YOU HAVE A GREAT PROCESSOR AND
# PLENTY OF MEMORY
"""
# So far this doesn't work, avoid using.
def parallel_process(X):
    pool = mp.Pool(processes=4)
    rand_inits = create_rand_variables(20)
    results = [pool.apply_async(k_means_process, args=(X, x[0], x[1], x[2])) for x in rand_inits]
    output = [p.get() for p in results]
    print(output)
"""


# Testing function that separates the bills based on their lengths
# TODO: Finish this
def separate_and_calc(bill_series):
    bill_unfiltered = pd.DataFrame(bill_series, columns=['text'])
    bill_unfiltered['lens'] = bill_series.apply(get_doc_lengths)
    print(bill_unfiltered.columns)
    # Function will split the dataset into several different ones to take a
    # focused look at the files.


def main():
    bill_series = get_series()
    bill_lens = [get_doc_lengths(bill) for bill in bill_series.tolist()]
    separate_and_calc(bill_series)
    try:
        hist(bill_lens, 'Lengths', 'bill_lengths')
    except FileNotFoundError:
        os.mkdir('visualizations')
        hist(bill_lens, 'Lengths', 'bill_lengths')
    box_plot(bill_lens, 'Lengths Box Plot', 'bill_lens_box')
    X = vectorize(bill_series)
    X = dimensionality_reduction(X, 100)
    # X = hashing_vector(bill_series)
    # cluster_tests_97(X)
    avg_scores = []
    for k in range(100, 200):
        distances, labels = clustering(X, k, slow=True)
        avg_score = evaluate_cluster(X, labels)
        print("Clusters: ", k, " Score: ", avg_score)
        avg_scores.append(avg_score)
        if avg_score > .2:
            save_clusters(bill_series.index, labels, distances, k)
            make_cluster_fig(distances, labels, k)
    # TODO: Figure out the best performing parameters for k-means
    print(max(avg_scores))
    
    
    hist(avg_scores, 'K-Means Silhouette Averages', 'silhouette_hist')
    box_plot(avg_scores, 'K-Means Silhouette Averages', 'silhouette_box')

if __name__ == '__main__':
    main()
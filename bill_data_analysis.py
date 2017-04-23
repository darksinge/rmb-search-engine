from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering
import os
import glob
#import multiprocessing as mp

import pandas as pd
#import numpy as np
from time import time
import random


def make_name(path):
    """
    Takes the file name and creates a readable name to make cluster searching much easier

    :param path:
    :return:
        string: an easy name to parse and search
    """
    doc_name = path.split('.txt')[0]
    split_doc = os.path.split(doc_name)
    year = os.path.split(split_doc[0])[-1]
    bill_name = split_doc[-1]
    name = year + bill_name
    return name



def get_series():
    """
    Finds the paths of all of the txt files in the database and adds their locations and names to a series

    Parameters:
        None

    Return:
         bill_series: a panda series full of the names of all of the txt files
    """
    time1 = time()
    data_files = []
    # TODO: Note that this is just for the year 2017, so when the full analysis needs to be done change to *
    data_folders = glob.glob(os.path.join('bill_files', 'filtered', '2017'))
    print(data_folders)
    for folder in data_folders:
        files = glob.glob(os.path.join(folder, '*.txt'))
        for f in files:
            data_files.append(f)
    bill_dict = {}
    for d in data_files:
        text = open(d)
        doc_name = make_name(d)
        print(doc_name)
        bill_dict[doc_name] = text.read()
        text.close()
    bill_series = pd.Series(bill_dict)
    print('Raw data read in {}s'.format(time() - time1))
    return bill_series


def vectorize(bill_series, save_vector=False):
    """
    Takes a series of text documents that have been read already and creates a tf-idf vector

    Parameters:
        bill_series: Pandas series with the text of each document
        save_vector: bool, if true the vector will be saved as a csv file

    Returns:
        Sparse matrix: A sparse matrix that can be used for clustering algorithms
    """
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


def hashing_vector(bill_series):
    """
    An alternate way to vectorize the documents. Previous testing has returned abysmal results for clustering, so not
    recommended.

    Parameters:
        bill_series: A series of strings for each document

    Returns:
        sparse matrix: A sparse matrix for clustering algorithms
    """
    time1 = time()
    vectorizer = HashingVectorizer(binary=True)
    X = vectorizer.fit_transform(bill_series)
    print('Vectorization done in {}s'.format(time() - time1))
    return X


def dimensionality_reduction(X, components):
    """
    Reduces dimensions of a sparse matrix using TruncatedSVD. So far this creates the best parameters
    for clustering, recommended to use prior to clustering. Other component analysis methods have not been tested,
    however.

    Parameters:
        X: Sparse matrix tf-idf vector
        components: How many components are being used for the SVD

    Return:
        A sparse matrix that has undergone dimension reduction. Speeds up clusterning and improves internal validity
        as well.
    """
    t0 = time()
    svd = TruncatedSVD(components)
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)
    
    X = lsa.fit_transform(X)
    
    print('Dimensionality reduction done in {}s'.format(time() - t0))
    print('Explained variance of the SVD step: {}'.format(svd.explained_variance_ratio_.sum()))
    return X


def clustering(X, clusters=4, max_iter=100, slow=False, init_size=2000, batch_size=2000, cluster_type="kmeans"):
    """
    Takes a tf-idf matrix and clusters it.

    Parameters:
        X: A sparse tf-idf matrix
        clusters: Integer. Number of clusters to be used
        max_iter: Integer. How many iterations to go before stopping
        slow: bool. Not used anymore. Use cluster_type instead
        init_size: Integer. If using the mini-kmeans batch, this determines the initialize size
        batch_size: Integer. Used for mini-kmeans batch
        cluster_type: String. Takes "kmeans" or "agg" currently. If the name isn't recognized your stuck with mini-
        kmeans

    Return:
        clustered_distances: a numpy array with two columns and rows for each document representing the distance between
            docs
        cluster_labels: a list with the cluster name for each doc.
    """
    time1 = time()
    if cluster_type == "kmeans":
        km = KMeans(n_clusters=clusters, max_iter=max_iter)
    elif cluster_type == "agg":
        cluster = AgglomerativeClustering(n_clusters=clusters, affinity="cosine", linkage="average")
        cluster.fit(X)
        print('Agglomerative clustering done in {}s'.format(time() - time1))
        return [], cluster.labels_
    else:
        km = MiniBatchKMeans(n_clusters=clusters, max_iter=max_iter, init_size=init_size, batch_size=batch_size)
    clustered_distances = km.fit_transform(X)
    cluster_labels = km.labels_
    print('KMeans clustering done in {}s'.format(time() - time1))
    return clustered_distances, cluster_labels


def evaluate_cluster(X, labels):
    """
    Uses the metric silhouette average to determine how well the documents have
    clustered. The metric can go from -1 (monkeys could have done it better) to 1 (did you cheat?). The closer to 1 the
    better. Compares how similar an object is to its cluster (cohesion) compared to other clusters (separation)

    Parameters:
        X: A sparse matrix
        labels: Labels returned from kmeans

    Return:
         float: a score -1 to 1 indicating internal validity
    """
    silhouette_avg =  silhouette_score(X, labels)
    return silhouette_avg


def make_cluster_fig(distances, labels, clusters):
    import matplotlib.pyplot as plt
    """
    Creates a scatter plot with the transformed distances of clustering

    Parameters:
        distances: numpy array with two columns for cluster distances (x, y)
        labels: the cluster each row corresponds to
        clusters: the number of clusters

    Return:
        None
    """
    time1 = time()
    fig, ax = plt.subplots()
    ax.scatter(x=distances[:, 0], y = distances[:, 1],c=labels)
    ax.set_title("Transformed Visualization of Document KMeans with {} Clusters".format(clusters))
    plt.savefig(os.path.join('visualizations','kmeans_{}k.png'.format(clusters)))
    plt.close()
    print("Visualization done in {}s".format(time() - time1))


def save_clusters(doc_names, labels, distances, num_clusters):
    """
    Saves the clusters with the corresponding document names as a csv, and includes the distances (nothing else)

    Parameters:
        doc_names: A series/list of the file names used
        labels: A list like structure of the cluster name for eacch document
        distances: numpy array with two columns with the distances of each cluster
        num_clusters: The number of clusters

    Return:
        None
    """
    time0 = time()
    df = pd.DataFrame({'cluster': labels, 'X': distances[:, 0], 'y': distances[:, 1]}, index=doc_names)
    if not os.path.exists(os.path.join('analysis', 'clusters')):
        os.mkdir(os.path.join('analysis', 'clusters'))
    df.sort_values('cluster', inplace=True)
    file_name = os.path.join('analysis', 'clusters', 'with_{}_clusters'.format(num_clusters))
    df.to_csv(file_name + '.csv')
    df.to_json(file_name + '.json')
    print("Cluster csv saved in {}s".format(time() - time0))
    

def get_doc_lengths(bill):
    """
    Gets the word length of the document

    Parameters
        bill: string of words in the document

    Returns:
        integer: the length of the text file
    """
    data = bill.split(' ')
    return len(data)


def hist(values, title, file_name):
    import matplotlib.pyplot as plt
    """
    Creates a histogram and saves a png to file in path -/visualizations for the sizes of documents. Right now the
    pictures kind of suck

    Parameters:
        values: length of documents
        title:
        file_name:

    Return:
        None
    """
    fix, ax = plt.subplots()
    ax.hist(values, bins=20)
    ax.set_title(title)
    ax.set_ylabel("Frequency")
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


def bar_graph(values, title, file_name):
    import matplotlib.pyplot as plt
    """
    Creates a bar_graph and saves a png

    Parameters:
        values: list-like structure with integers for document lengths.
        title: Title to give the graph
        file_name: What to save the file as

    Returns:
        None
    """
    fig, ax = plt.subplots()
    ax.bar([.25 + x for x in range(len(values))], values)
    ax.set_title(title)
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


def box_plot(values, title, file_name):
    import matplotlib.pyplot as plt
    """
    Function creates a box plot and saves it to a file in path -/visualizations/
    Bar graph and box plot could be combined. They will be in the future.

    Parameters:
        values: list-like structure with
        title: Title to give the plot
        file_name: What to save it as

    Return:
        None
    """
    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_title(title)
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


def cluster_tests(X, k):
    """
    This is slow, only for testing purposes
    Used to test different parameters with a fixed k

    Parameters:
        X: sparse-matrix tf-idf
        k: Number of clusters

    Return:
        None
    """
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


# DANGER ZONE!!!!!!!
def k_means_process(X, k, init_size, batch_size):
    """
    Was used for a multi-threading process, but so far is not usable
    Don't use unless you fix that other stuff.

    Parameters:
        X: spare matrix tf-idf structure
        k: Number of clusters
        init_size: Int for the size if we are using kmeans-mini batch
        batch_size: Used for kmeans-mini batch

    Return:
        output.put()
    """
    distances, labels = clustering(X, k, init_size, batch_size)
    avg_score = evaluate_cluster(X, labels)
    if avg_score > .2:
        make_cluster_fig(distances, labels, k)
    return (k, avg_score, init_size, batch_size)
    #output.put()
    

# TESTING
def create_rand_variables(size):
    """
    Creates a list with variables for to send to k_means_process. Just for experimenting to find the perfect parameters.

    Parameters:
        size: What's the range you want?

    Returns:
        lst: a list with variables for each run of the kmeans algorithm.
    """
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


def separate_and_calc(bill_series):
    """
    Testing function that separates the bills based on their lengths. This way more meaningful graphs can be created of
    the word lengths. Unfinished, at this point may just be dropped.

    Parameters:
        bill_series: Bill documents

    Return:
        None, for now
    """
    bill_unfiltered = pd.DataFrame(bill_series, columns=['text'])
    bill_unfiltered['lens'] = bill_series.apply(get_doc_lengths)
    print(bill_unfiltered.columns)
    # Function will split the dataset into several different ones to take a
    # focused look at the files.


def start_analysis():
    bill_series = get_series()
    """
    bill_lens = [get_doc_lengths(bill) for bill in bill_series.tolist()]
    separate_and_calc(bill_series)

    # Creates visualizations of the bill lengths, not needed for kmeans analysis
    try:
        hist(bill_lens, 'Lengths', 'bill_lengths')
    except FileNotFoundError:
        os.mkdir('visualizations')
        hist(bill_lens, 'Lengths', 'bill_lengths')
    box_plot(bill_lens, 'Lengths Box Plot', 'bill_lens_box')
    """

    X = vectorize(bill_series, save_vector=True)
    X = dimensionality_reduction(X, 100)
    max_score = 0
    max_cluster = None
    max_k = 0
    # Finds and saves the best clustering based on performance
    for k in range(125, 130):
        distances, labels = clustering(X, k, slow=True)
        avg_score = evaluate_cluster(X, labels)
        if avg_score > max_score:
            max_score = avg_score
            max_cluster = (distances, labels)
            max_k = k
    print("Best performing cluster: ", max_k, ' ', max_score)
    save_clusters(bill_series.index, max_cluster[1], max_cluster[0], 'max')


if __name__ == '__main__':
    start_analysis()
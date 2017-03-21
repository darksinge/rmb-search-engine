from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans, MiniBatchKMeans
import os
import glob
import pandas as pd
from time import time
import matplotlib.pyplot as plt


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

def clean_terms(string):
    pass


def vectorize(bill_series):
    time1 = time()
    vectorizer = TfidfVectorizer(max_df=.4, min_df=2, stop_words='english')
    X = vectorizer.fit_transform(bill_series)
    print('Vectorization done in {}s'.format(time() - time1))
    return X


def hashing_vector(bill_series):
    time1 = time()
    vectorizer = HashingVectorizer(binary=True)
    X = vectorizer.fit_transform(bill_series)
    print('Vectorization done in {}s'.format(time() - time1))
    return X


def clustering(X, clusters=4, max_iter=100, slow=False, init_size=2000, batch_size=2000):
    time1 = time()
    # Uses MiniBatchKMeans, which is a faster implementation of KMeans clustering that performs slightly lower than the
    # original
    if slow:
        km = KMeans(n_clusters=clusters, max_iter=max_iter)
    else:
        km = MiniBatchKMeans(n_clusters=clusters, max_iter=max_iter, init_size=init_size, batch_size=batch_size)
    clustered_distances = km.fit_transform(X)
    cluster_labels = km.labels_
    print('KMeans clustering done in {}s'.format(time() - time1))
    return clustered_distances, cluster_labels


def evaluate_cluster(X, labels):
    silhouette_avg =  silhouette_score(X, labels)
    return silhouette_avg


def make_cluster_fig(distances, labels, clusters):
    time1 = time()
    fig, ax = plt.subplots()
    ax.scatter(x=distances[:, 0], y = distances[:, 1],c=labels)
    ax.set_title("Transformed Visualization of Document KMeans with {} Clusters".format(clusters))
    plt.savefig(os.path.join('visualizations','kmeans_{}k.png'.format(clusters)))
    plt.close()
    print("Visualization done in {}s".format(time() - time1))


def get_doc_lengths(bill):
    data = bill.split(' ')
    # TODO: The documents could be cleaned a little, a lot of them have information that isn't important for our
    # analysis, such as lists (i.e. '(a) ... (b)') as words
    return len(data)


def hist(values, title, file_name):
    fix, ax = plt.subplots()
    ax.hist(values, bins=20)
    ax.set_title(title)
    ax.set_ylabel("Frequency")
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


def bar_graph(values, title, file_name):
    fig, ax = plt.subplots()
    ax.bar([.25 + x for x in range(len(values))], values)
    ax.set_title(title)
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


def box_plot(values, title, file_name):
    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_title(title)
    plt.savefig(os.path.join('visualizations', file_name + '.png'))
    plt.close()


def cluster_tests_97(X):
    scores_by_init = {}
    """
    print('-------------------init_size-------------')
    for i in range(500, 10000, 100):
        distances, labels = clustering(X, 97, init_size=i)
        avg_score = evaluate_cluster(X, labels)
        print("Score: ", avg_score, 'Size: ', i)
        scores_by_init[i] = avg_score

    print('-------------------batch-----------------')
    scores_by_batch = {}
    for i in range(500, 10000, 100):
        distances, labels = clustering(X, 97, init_size=2700, batch_size=i)
        avg_score = evaluate_cluster(X, labels)
        print("Score: ", avg_score, 'Batch: ', i)
        scores_by_batch[i] = avg_score

    for i in range(500, 10000, 100):
        distances, labels = clustering(X, 97, init_size=i, batch_size=i)
        avg_score = evaluate_cluster(X, labels)
        print("Score: ", avg_score, 'Batch: ', i)
        """


def main():
    bill_series = get_series()
    bill_lens = [get_doc_lengths(bill) for bill in bill_series.tolist()]
    hist(bill_lens, 'Lengths', 'bill_lengths')
    box_plot(bill_lens, 'Lengths Box Plot', 'bill_lens_box')
    X = vectorize(bill_series)
    # X = hashing_vector(bill_series)
    # cluster_tests_97(X)
    avg_scores = []

    for i in range(20, 30):
        distances, labels = clustering(X, i)
        avg_score = evaluate_cluster(X, labels)
        print("Clusters: ", i, " Score: ", avg_score)
        avg_scores.append(avg_score)
        if avg_score > .2:
            print('Decent Average Score!')
            make_cluster_fig(distances, labels, i)
    print(max(avg_scores))
    hist(avg_scores, 'K-Means Silhouette Averages', 'silhouette_hist')
    box_plot(avg_scores, 'K-Means Silhouette Averages', 'silhouette_box')

if __name__ == '__main__':
    main()
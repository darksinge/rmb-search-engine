import os
from configs import default_path


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
    fig, ax = plt.subplots()
    ax.scatter(x=distances[:, 0], y = distances[:, 1],c=labels)
    ax.set_title("Transformed Visualization of Document KMeans with {} Clusters".format(clusters))
    plt.savefig(os.path.join(default_path, 'visualizations','kmeans_{}k.png'.format(clusters)))
    plt.close()


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
    plt.savefig(os.path.join(default_path, 'visualizations', file_name + '.png'))
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
    plt.savefig(os.path.join(default_path, 'visualizations', file_name + '.png'))
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
    plt.savefig(os.path.join(default_path, 'visualizations', file_name + '.png'))
    plt.close()
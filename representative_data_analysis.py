# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 09:51:38 2017
@author: Bradley Robinson
Analyzes each session and clusters the representatives based on groups. Note that it is not up to date for server use,
must be ran locally
"""
import pandas as pd
from sklearn.cluster import KMeans
from default_path import default_path
from bokeh.plotting import figure, output_file, save
from bokeh.charts import Scatter
import glob
import os


def get_color_by_label(label):
    if label == 0:
        return 'lightcoral'
    else:
        return 'darkblue'

def make_images(distances, labels, name):

    fig_directory = os.path.join(default_path, 'visualizations', 'rep_clusters')
    for year in glob.glob(os.path.join('analysis', 'rep_clusters', '*.csv')):
        if not os.path.exists(fig_directory):
            os.mkdir(fig_directory)
        df = pd.read_csv(year)
        df['colors'] = df['clusters'].apply(get_color_by_label)
        cur_name = os.path.split(year)[-1][0:5]
        plot = Scatter(df, x='X', y='y', color='colors')
        output_file(os.path.join(fig_directory, cur_name + '.html'))
        save(plot)
    """
    fig, ax = plt.subplots()
    ax.scatter(x, y, c=labels)
    plt.savefig(os.path.join('visualizations', name+'.png'))
    plt.close()
    """


def save_spreadsheets(distances, labels, representatives, name):
    new_df = pd.DataFrame({'reps': representatives})
    new_df['X'] = distances[:,0]
    new_df['y'] = distances[:,1]
    new_df['clusters'] = labels
    csv_directory = os.path.join(default_path, 'analysis', 'rep_clusters')
    if not os.path.exists(csv_directory):
        os.mkdir(csv_directory)
    new_df.to_csv(os.path.join(csv_directory, name + '.csv'))
    
    
def clustering(df):
    km = KMeans(n_clusters=2)
    columns = df.columns[2:]
    distances = km.fit_transform(df[columns])
    labels = km.labels_
    return distances, labels


def get_dfs():
    files = glob.glob(os.path.join(default_path, 'voting', '*.csv'))
    dfs = {}
    for f in files:
        df = pd.read_csv(f)
        f_name = os.path.split(f)[1]
        name = f_name.split('.csv')[0]
        if df.shape[0] > 0:
            dfs[name] = df
    return dfs
    

def cluster_list(dfs):
    for name, df in dfs.items():
        X, labels = clustering(df)
        save_spreadsheets(X, labels, df['Representatives'], name)
    make_images(X, 'a', "n")
    

def main():
    dfs = get_dfs()
    cluster_list(dfs)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 09:51:38 2017
@author: Bradley Robinson
Analyzes each session and clusters the representatives based on groups
"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
import glob
import os


def make_image(distances, labels, name):
    x = distances[:,0]
    y = distances[:,1]
    fig, ax = plt.subplots()
    ax.scatter(x, y, c=labels)
    plt.savefig(os.path.join('visualizations', name+'.png'))
    plt.close()


def save_spreadsheets(distances, labels, representatives, name):
    new_df = pd.DataFrame({'reps': representatives})
    new_df['X'] = distances[:,0]
    new_df['y'] = distances[:,1]
    new_df['clusters'] = labels
    new_df.to_excel(os.path.join('analysis', 'rep_clusters', name+'.xlsx'))
    
    
def clustering(df):
    km = KMeans(n_clusters=2)
    columns = df.columns[2:]
    distances = km.fit_transform(df[columns])
    labels = km.labels_
    return distances, labels


def get_dfs():
    files = glob.glob(os.path.join('voting', '*.csv'))
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
        make_image(X, labels, name)
        save_spreadsheets(X, labels, df['Representatives'], name)
    

def main():
    dfs = get_dfs()
    cluster_list(dfs)
    


if __name__ == '__main__':
    main()

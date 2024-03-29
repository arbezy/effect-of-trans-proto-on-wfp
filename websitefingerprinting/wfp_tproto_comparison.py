from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

from joblib import dump

import pandas as pd
import numpy as np

from math import floor

def main():
    for h_version in ["h2", "h3"]:
        #print(h_version)
        classifiers = [ExtraTreesClassifier(), RandomForestClassifier(), KNeighborsClassifier(), GaussianNB(), SVC()]
        clf_strs = ["extra_trees", "rand_forest", "KNN", "GaussianNB", "SVC"]
        clf_results = {s:[] for s in clf_strs}
        for c_i in range(len(classifiers)):
            print(clf_strs[c_i])
            my_range = range(5,205,5)
            simple_results = [[] for i in my_range]
            transfer_results = [[] for i in my_range]
            for j in my_range:
                # SIMPLE:
                labels, streams = get_simple_wfp_data(h_version, j)
                cv = KFold(n_splits=10, shuffle=True)
                cross_val_scores = cross_val_score(classifiers[c_i], streams, labels, cv=cv, scoring="accuracy")
                mean_score = cross_val_scores.mean()
                std_dev = cross_val_scores.std()
                simple_results[floor(j/5)-1].append(mean_score)
                #print(f"simple done for k={j}")
                
                # TRANSFER:
                labels, streams = get_transfer_wfp_data(h_version, j)
                cv = KFold(n_splits=10, shuffle=True)
                cross_val_scores = cross_val_score(classifiers[c_i], streams, labels, cv=cv, scoring="accuracy")
                mean_score = cross_val_scores.mean()
                std_dev = cross_val_scores.std()
                transfer_results[floor(j/5)-1].append(mean_score)
                #print(f"transfer done for k={j}")
                
            clf_results[clf_strs[c_i]].append(simple_results)
            clf_results[clf_strs[c_i]].append(transfer_results)
        
        print("HTTP VERSION="+h_version)
        for k in clf_results:
            print(k)
            print("SIMPLE:")
            print(clf_results[k][0])
            print("TRANSFER:")
            print(clf_results[k][1])

# TODO: exclude ustc
def get_transfer_wfp_data(h_version: str, k: int):
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        d_df = df[df['0'] == d]
        new_df = pd.concat([new_df, d_df[:100]])
        
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, 8:]
    return labels, streams

def get_simple_wfp_data(h_version: str, k: int):
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        d_df = df[df['0'] == d]
        new_df = pd.concat([new_df, d_df[:100]])
        
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, :8]
    #print(streams)
    return labels, streams

main()
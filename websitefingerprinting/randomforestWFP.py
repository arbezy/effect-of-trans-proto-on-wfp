# WEBSITE FINGERPRINTING

# MY OS (win32) IS NOT COMPATIBLE WITH AUTOSKLEARN -> use a docker container for this
# need to use a linux operating system

#import autosklearn.classification
#autosklearn.classification.AutoSklearnClassifier()

# import sklearn.model_selection
# import sklearn.datasets
# import sklearn.metrics

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
#import xgboost as xgb

from sklearn.pipeline import Pipeline

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import top_k_accuracy_score
from sklearn.metrics import make_scorer

from sklearn import preprocessing

from joblib import dump

# import random

import pandas as pd
import numpy as np

from math import floor

# EARLY QUIC paper uses just the simple features when doing a top-k attack

def main():
    for h_version in ['h2' ,'h3']:
        final_results = []
        for j in range(5, 45, 5):
            # Fetch data:
            #labels, streams = get_wfp_data(j)
            labels, streams = get_simple_wfp_data(h_version, j)
            print(f"labels and streams fetched from k={j} feature csv")
            
            # Creating model WITH cross validation
            # could pipe multiple models in here
            # model_pipeline = Pipeline(steps=[('model', RandomForestClassifier())])
            temp_results = []
            for i in range(1,6):
                clf = RandomForestClassifier()
                cv = KFold(n_splits=10, shuffle=True, random_state=42)
                top_k_accuracy_scorer = make_scorer(
                    top_k_accuracy_score,
                    response_method=("decision_function", "predict_proba"),
                    greater_is_better=True,
                    k=i
                )
                
                cross_val_scores = cross_val_score(clf, streams, labels, cv=cv, scoring=top_k_accuracy_scorer)
                #cross_val_scores = cross_val_score(clf, streams, labels, cv=cv)
                
                mean_score = cross_val_scores.mean()
                std_dev = cross_val_scores.std()
                
                print(f"top-{i} accuracy, first {j} packets")
                print(cross_val_scores)
                print(f"mean:{mean_score} std_dev:{std_dev}\n")

                mean_and_dev = str(round(mean_score*100, 3)) + "+/-" + str(round(std_dev*100, 3))
                print(mean_and_dev)
                temp_results.append(mean_and_dev)
            final_results.append(temp_results)

        print("\n")
        print(f"HTTP VERSION={h_version}")
        for i in range(len(final_results)):
            print(final_results[i])

def get_wfp_data(h_version: str, k: int):
    print("SIMPLE + TRANSFER FEATURES")
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    # in the paper they only use 92 sites
    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        # Excluding ustc, as it slipped though the cracks and made it into my extracted feature data
        if d != 'ustc':
            d_df = df[df['0'] == d]
            new_df = pd.concat([new_df, d_df[:100]])
        
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1)
    return labels, streams

def get_simple_wfp_data(h_version: str, k: int):
    print("SIMPLE FEATURES")
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    # in the paper they only use 92 sites
    domains = df['0'].unique()
    #print(f"# of domains = {len(domains)}")
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        if d != 'ustc':
            d_df = df[df['0'] == d]
            new_df = pd.concat([new_df, d_df[:100]])
            
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, :8]
    #print(streams)
    return labels, streams

def get_transfer_wfp_data(h_version: str, k: int):
    print("TRANSFER FEATURES")
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    # in the paper they only use 92 sites
    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        if d != 'ustc':
            d_df = df[df['0'] == d]
            new_df = pd.concat([new_df, d_df[:100]])
        
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, 8:]
    return labels, streams

main()
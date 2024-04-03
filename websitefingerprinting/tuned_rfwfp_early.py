

from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score
from sklearn.metrics import top_k_accuracy_score
from sklearn.metrics import make_scorer

from sklearn import preprocessing

# used for saving models
from joblib import dump

import pandas as pd
import numpy as np

from math import floor

def main():
    # ['h2' ,'h3']:
    for h_version in ['h2','h3']:
        final_results = []
        # range of values to use for n (the no. of packets considered i.e. n=10, the first 10 packets)
        for j in range(5, 45, 5):
            # Fetch simple features:
            labels, streams = get_simple_wfp_data(h_version, j)
            print(f"labels and streams fetched from k={j} feature csv")
            
            temp_results = []
            for i in range(1,6):
                # using different hyperparams for each model, as different ones found during tuning for each protocol
                if h_version == 'h2':
                    clf = RandomForestClassifier(max_depth=20, max_features=None, min_samples_leaf=1, min_samples_split=10, n_estimators=500)
                else:
                    clf = RandomForestClassifier(max_depth=20, max_features='log2', min_samples_leaf=2, min_samples_split=5, n_estimators=500)
                    
                # 10 fold cross validation:
                # setting the random state so that both protocols have the same one.
                cv = KFold(n_splits=10, shuffle=True, random_state=42)
                
                # make top-k scorer with different values of k:
                top_k_accuracy_scorer = make_scorer(
                    top_k_accuracy_score,
                    response_method=("decision_function", "predict_proba"),
                    greater_is_better=True,
                    k=i
                )

                # get top-k scores for each fold
                cross_val_scores = cross_val_score(clf, streams, labels, cv=cv, scoring=top_k_accuracy_scorer)
                
                mean_score = cross_val_scores.mean()
                std_dev = cross_val_scores.std()
                
                print(f"top-{i} accuracy, first {j} packets")
                print(cross_val_scores)
                print(f"mean:{mean_score} std_dev:{std_dev}\n")

                temp_results.append(mean_score)
            final_results.append(temp_results)

        print("\n")
        print(f"HTTP VERSION={h_version}")
        for i in range(len(final_results)):
            print(final_results[i])

def get_simple_wfp_data(h_version: str, k: int):
    print("SIMPLE FEATURES")
    # traffic features calculated WITHOUT HANDSHAKE!
    df = pd.read_csv(f"D:/traffic_features_wo_handshake/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    domains = df['0'].unique()
    #print(f"# of domains = {len(domains)}")
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        if d != 'ustc':
            d_df = df[df['0'] == d]
            # only use 100 traces per domain, no more.
            new_df = pd.concat([new_df, d_df[:100]])
            
    labels = new_df['0']
    # get just the simple features...
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, :8]
    #print(streams)
    return labels, streams

main()
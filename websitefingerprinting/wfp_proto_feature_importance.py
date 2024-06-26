print("hello")

# TODO: Copy across wfp_tproto_comparison


# Feature importance code... for diabetes dataset

from sklearn import datasets
diabetes = datasets.load_diabetes()
print(diabetes.feature_names)
# from sklearn.model_selection import cross_validate
# from sklearn.svm import LinearSVC
# from sklearn.ensemble import  RandomForestClassifier
# import pandas as pd

# diabetes = datasets.load_diabetes()
# X, y = diabetes.data, diabetes.target

# clf=RandomForestClassifier(n_estimators =10, random_state = 42, class_weight="balanced")
# output = cross_validate(clf, X, y, cv=2, scoring = 'accuracy', return_estimator =True)

# for idx,estimator in enumerate(output['estimator']):
#     print("Features sorted by their score for estimator {}:".format(idx))
#     feature_importances = pd.DataFrame(estimator.feature_importances_,
#                                        index = diabetes.feature_names,
#                                         columns=['importance']).sort_values('importance', ascending=False)
#     print(feature_importances)
    
# end.

# Add this code into copy of wfp_tproto_comparison, take out the sorting bit though as im trying to graph this mfer


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

# TODO: test, then write code to record the feature importances to a dataframe, which is saved then can be used for plotting...

def main():
    for h_version in ["h2", "h3"]:
        #print(h_version)
        classifiers = [ExtraTreesClassifier(), RandomForestClassifier(), KNeighborsClassifier(), GaussianNB(), SVC()]
        classifiers = [RandomForestClassifier()]
        clf_strs = ["extra_trees", "rand_forest", "KNN", "GaussianNB", "SVC"]
        clf_results = {s:[] for s in clf_strs}
        for c_i in range(len(classifiers)):
            print(clf_strs[c_i])
            my_range = range(5,10,5)
            simple_results = [[] for i in my_range]
            transfer_results = [[] for i in my_range]
            for j in my_range:
                # SIMPLE:
                labels, streams = get_simple_wfp_data(h_version, j)
                cv = KFold(n_splits=10, shuffle=True)
                output = cross_validate(classifiers[c_i], streams, labels, cv=cv, scoring="accuracy", return_estimator=True)
                for idx,estimator in enumerate(output['estimator']):
                    print("Features sorted by their score for estimator {}:".format(idx))
                    feature_importances = pd.DataFrame(estimator.feature_importances_,
                                                        index = streams.columns,
                                                        columns=['importance'])
                    print(feature_importances)
                #print(f"simple done for k={j}")
                
                # TRANSFER:
                labels, streams = get_transfer_wfp_data(h_version, j)
                cv = KFold(n_splits=10, shuffle=True)
                output = cross_val_score(classifiers[c_i], streams, labels, cv=cv, scoring="accuracy", return_estimator=True)
                for idx,estimator in enumerate(output['estimator']):
                    print("Features sorted by their score for estimator {}:".format(idx))
                    feature_importances = pd.DataFrame(estimator.feature_importances_,
                                                        index = streams.columns,
                                                        columns=['importance'])
                    print(feature_importances)
                #print(f"transfer done for k={j}")
                
            clf_results[clf_strs[c_i]].append(simple_results)
            clf_results[clf_strs[c_i]].append(transfer_results)
        
        print("HTTP VERSION="+h_version)
        for k in clf_results:
            print(k)
            print("SIMPLE:")
            print(clf_results[k][0])
            # print("SIMPLE FEATURE IMPORTANCE:")
            # print()
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
    # NOTE: may need to collect multidim features into a single col, so that I can label it in order to get feature importances per feature
     # ((1460)*2) + (k*2) + (1*7)
    cols = ['unique_pkt_size' for _ in range(1460)] + ['pkt_size_counts' for _ in range(1460)] + ['ordered_pkt_lengths' for _ in range(k)] + ['interarrival_time' for _ in range(k)]
    cols = cols + ['negative_pkts'] + ['cumulative_sum'] + ['cumulative_sum_w_direction'] + ['bursts', 'max_burst', 'mean_burst'] + ['total_transmission_time']
    streams.columns = cols
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
    streams.columns = ['pt', 'ps','pm','pl','nt','ns','nm','nl']
    return labels, streams

main()
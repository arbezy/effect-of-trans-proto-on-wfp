from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV

from joblib import dump

import pandas as pd
import numpy as np

from math import floor

import datetime

# Grid search to tune hyperparameters on k=200 (first 200 packets)

def main():
    classifiers = [ExtraTreesClassifier(), RandomForestClassifier(), KNeighborsClassifier(), GaussianNB(), SVC()]
    clf_strs = ["extra_trees", "rand_forest", "KNN", "GaussianNB", "SVC"]
    
    # ~~~temp!!!!~~~
    classifiers = classifiers[:2]
    clf_strs = clf_strs[:2]
    # ~~~~~~~~~~~~~~
    
    grids = []
    max_depth_arr = [int(x) for x in np.linspace(10, 110, num=11)]
    max_depth_arr.append(None)
    et_grid = {
        'n_estimators':[100,200,300,400,500],
        'max_features':[None, 'sqrt', 'log2'],
        'max_depth' : max_depth_arr,
        'min_samples_split' : [2,5,10],
        'min_samples_leaf' : [1,2,4],
    }
    
    rf_grid = {
        'n_estimators':[100,200,300,400,500],
        'max_features':[None, 'sqrt', 'log2'],
        'max_depth' : max_depth_arr,
        'min_samples_split' : [2,5,10],
        'min_samples_leaf' : [1,2,4],
    }
    
    knn_grid = {
        'n_neighbors' : list(range(1, 50, 2))
    }
    
    nb_grid = {
        'var_smoothing' : np.logspace(0,-9,num=100)
    }
    
    svc_grid = {
        'C' : [0.1, 1, 10, 100, 1000],
        'gamma' : [1, 0.1, 0.01, 0.001, 0.0001],
    }
    
    grids.append(et_grid)
    grids.append(rf_grid)
    grids.append(knn_grid)
    grids.append(nb_grid)
    grids.append(svc_grid)
    
    # ["h2", "h3"]
    for h_version in ["h2"]: 
        for c_i in range(len(classifiers)):
            print(f"HTTPVERSION={h_version}, CLASSIFIER={clf_strs[c_i]}")
            print(f"datetime={datetime.datetime.now()}")
            
            # SIMPLE:
            labels, streams = get_simple_wfp_data(h_version)
            my_cv = KFold(n_splits=5, shuffle=True)
            gs_cv = GridSearchCV(estimator=classifiers[c_i], param_grid=grids[c_i], cv=my_cv)
            gs_cv.fit(streams, labels)
            print(f"best simple params for {clf_strs[c_i]}: {gs_cv.best_params_}\n")
            
            # print(f"datetime={datetime.datetime.now()}")
                        
            # # TRANSFER:
            # labels, streams = get_transfer_wfp_data(h_version)
            # my_cv = KFold(n_splits=3, shuffle=True)
            # gs_cv = GridSearchCV(estimator=classifiers[c_i], param_grid=grids[c_i], cv=my_cv)
            # gs_cv.fit(streams, labels)
            # print(f"best transfer params for {clf_strs[c_i]}: {gs_cv.best_params_}\n")

def get_transfer_wfp_data(h_version: str):
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_200.csv")
    df = df.sort_values(['0'])

    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        d_df = df[df['0'] == d]
        new_df = pd.concat([new_df, d_df[:100]])
        
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, 8:]
    return labels, streams

def get_simple_wfp_data(h_version: str):
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_200.csv")
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
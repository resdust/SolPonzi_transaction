import numpy as np
import pandas as pd
import tools as tl
import os
# from arff2pandas import a2p
from scipy import stats
import json
import time
from sklearn import preprocessing
import matplotlib.pyplot as plt

t0 = time.process_time()

print("define variable and load data")
path = os.path
ponzi = path.join('feature','ponzi_feature.csv')
nponzi = path.join('feature','nponzi_feature.csv')

def extract():
    database_ponzi = path.join('feature','nponzi_feature_raw.csv')

    raw_data = pd.read_csv(database_ponzi,index_col='index')
    raw_data = raw_data.fillna(0)
    tx_features = []
    f_names = ['ponzi',
                'nbr_tx_in',
                'nbr_tx_out', 
                'Tot_in', 
                'Tot_out',
                'mean_in',
                'mean_out',
                'sdev_in',
                'sdev_out',
                'gini_in',
                'gini_out',
                'avg_time_btw_tx',
                # 'gini_time_out',
                'lifetime',
                ]
    for i in range(raw_data.shape[0]):
        ponzi = raw_data.iloc[i]['ponzi']
        time_in = raw_data.iloc[i]['time_in']
        time_out = raw_data.iloc[i]['time_out']
        val_in = raw_data.iloc[i]['val_in']
        val_out = raw_data.iloc[i]['val_out']
        if val_in != '' or val_out != '':
            f = tl.basic_features(ponzi,time_in, time_out, val_in, val_out)
            tx_features.append(f)

    tl.compute_time(t0)

    df_features = pd.DataFrame(tx_features,columns=f_names)
    f_file = nponzi
    df_features.to_csv(f_file,index=None)
    print('---Have written feature file '+ f_file+'.---')

def combine(f1,f2,w_file):
    df1 = pd.read_csv(f1)
    df2 = pd.read_csv(f2)
    df = pd.concat([df1,df2],axis=0)
    df.to_csv(w_file,index=False)
    print('-----Written '+w_file+'-----')

combine(ponzi,nponzi,path.join('feature','train.csv'))
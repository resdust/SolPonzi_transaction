import numpy as np
import pandas as pd
import tools as tl
import color
import os
# from arff2pandas import a2p
from scipy import stats
import json
import time
from sklearn import preprocessing
import matplotlib.pyplot as plt

t0 = time.process_time()


def extract(database):
    # database_ponzi = path.join('feature','nponzi_feature_raw.csv')
    color.pInfo("Dealing with transaction data data")

    raw_data = pd.read_csv(database)
    raw_data = raw_data.fillna(0)
    tx_features = []
    f_names = [#'ponzi',
                'address',
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
        # ponzi = raw_data.iloc[i]['ponzi']
        address = raw_data.iloc[i]['address']
        time_in = raw_data.iloc[i]['time_in']
        time_out = raw_data.iloc[i]['time_out']
        val_in = raw_data.iloc[i]['val_in']
        val_out = raw_data.iloc[i]['val_out']
        if val_in != '' or val_out != '':
            #f = tl.basic_features(ponzi, time_in, time_out, val_in, val_out)
            f = tl.basic_features(None,address, time_in, time_out, val_in, val_out)
            tx_features.append(f)

    tl.compute_time(t0)

    df_features = pd.DataFrame(tx_features,columns=f_names)
    name = os.path.basename(database).split('.')[0]
    f_file = os.path.join('feature',name.split('_')[0]+'_'+name.split('_')[1]+'_feature.csv')
    df_features.to_csv(f_file,index=None)
    color.pDone('Have written feature file '+ f_file+'.')

def combine(f1,f2,w_file):
    df1 = pd.read_csv(f1)
    df2 = pd.read_csv(f2)
    df = pd.concat([df1,df2],axis=0)
    df.to_csv(w_file,index=False)
    color.pDone('Written '+w_file+'.')

if __name__=='__main__':
    path = os.path
    ponzi = path.join('feature','ponzi_feature.csv')
    nponzi = path.join('feature','nponzi_feature.csv')
    extract(path.join('result','test_12_database.csv')) 

#coding=utf-8
import pandas as pd
f_names = [ 'address',
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
            'prediction margin',
            'predicted ponzi',
            'ponzi'
            ]
def arff_to_csv(fpath):
    #读取arff数据
    if fpath.find('.arff') <0:
        print('the file is nott .arff file')
        return
    f = open(fpath)
    lines = f.readlines()
    content = []
    for l in lines:
        content.append(l)
    datas = []
    for c in content:
        if c!='' and c[0]!='@' and c!='\n':
            cs = c.split(',')
            cs[-1] = cs[-1].strip()
            datas.append(cs)

    #将数据存入csv文件中
    df = pd.DataFrame(data=datas,index=None,columns=f_names)
    filename = fpath[:fpath.find('.arff')] + '.csv'
    df.to_csv(filename,index=None)

arff_to_csv('train-ponzi+dapp2_result-RF.arff')
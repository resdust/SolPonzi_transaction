import numpy as np
import pandas as pd
from sklearn import metrics

# [[TP,FP],[FN,TN]]

df = pd.read_csv('test result.csv') # [address, symbolic checked, behavior predicted, Ponzi]

metric_names = ['accuracy','precision','recall','f1-score','AUC']

results = []

def basic_metrics(results,y_true,y_pred):
    r = []

    r.append(round(metrics.accuracy_score(y_true,y_pred),3))
    r.append(round(metrics.precision_score(y_true,y_pred),3))
    r.append(round(metrics.recall_score(y_true,y_pred),3))
    r.append(round(metrics.f1_score(y_true,y_pred),3))
    r.append(round(metrics.auc(y_true,y_pred),3)) # AUC
    results.append(r)

# return [tp,fp,tn,fn],fail/len(y_pred)
def confusion(y_true,y_pred):
    tp=0
    fp=0
    tn=0
    fn = 0
    fail = 0
    for i in range(len(y_pred)):
        if y_true[i]==y_pred[i]:
            if y_true[i]==1:
                tp = tp+1
            else:
                tn = tn+1
        else:
            if y_true[i]==1:
                fn = fn+1
            else:
                fp = fp+1
        if y_pred[i]=='failed':
            fail = fail+1

    Rsd = 1-fail/len(y_pred)
    print(Rsd)
    return [tp,fp,tn,fn],Rsd

def plot_PR(y_true,y_scores):
    import matplotlib.pyplot as plt
    
    precision, recall, thresholds = metrics.precision_recall_curve(y_true, y_scores)
    plt.figure("P-R Curve")
    plt.title('Precision/Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.plot(recall,precision)
    plt.show()

def syn(datas):
    y_ture = datas[:,3]
    y_pred = []
    for data in datas:
        if data[2] != 'failed':
            if data[1] != 'failed':
                if data[2] == '1':
                    y_pred.append(data[1])
                else:
                    y_pred.append(data[2])
            else:
                y_pred.append(data[2])
        else:
            if data[1] != 'failed':
                y_pred.append(data[1])
            else:
                y_pred.append('failed')

    return y_ture, y_pred

def single():
    basic_metrics(results,y_true_sym,y_sym)
    basic_metrics(results,y_true_bhv,y_bhv)
    basic_metrics(results,y_true_syn,y_syn)
    
    results.append([round(r*r_sym,3) for r in results[0]])
    results.append([round(r*r_bhv,3) for r in results[1]])
    results.append([round(r*r_syn,3) for r in results[2]])

y_ture_syn,y_pred_syn = syn(df.values)

syn = {'synthetical predicted':y_pred_syn,'Ponzi':y_ture_syn}
df_syn = pd.DataFrame(syn)
# syn_results.to_csv('synthetical results.csv',index=False)

mtx_sym, r_sym = confusion(df['Ponzi'].values,df['symbolic checked'].values)
mtx_bhv, r_bhv = confusion(df['Ponzi'].values,df['behavior predicted'].values)
mtx_syn, r_syn = confusion(y_ture_syn, y_pred_syn)

# mtx = {'SymChecker':mtx_sym,'BehaviorChecker':mtx_bhv,'Synthetical':mtx_syn}
# df_mtx = pd.DataFrame(mtx)
# df_mtx=df_mtx.T
# df_mtx.columns = ['TP','FP','TN','FN']
# df_mtx.to_csv('confusion matrix.csv')

# df_sym = pd.read_csv('symbolic result.csv')
# df_bhv = pd.read_csv('behavior result.csv')
# df_syn = pd.read_csv('synthetical results-delete failed.csv')

df_sym=df[~df['symbolic checked'].isin(['failed'])]
df_bhv=df[~df['behavior predicted'].isin(['failed'])]
df_syn=df_syn[~df_syn['synthetical predicted'].isin(['failed'])]

y_true_sym = df_sym['Ponzi'].values.astype(np.int)
y_sym = df_sym['symbolic checked'].values
y_sym = y_sym.astype(np.int)
y_true_bhv = df_bhv['Ponzi'].values.astype(np.int)
y_bhv = df_bhv['behavior predicted'].values
y_bhv = y_bhv.astype(np.int)
y_true_syn = df_syn['Ponzi'].values.astype(np.int)
y_syn = df_syn['synthetical predicted'].values
y_syn = y_syn.astype(np.int)
single()

res = pd.DataFrame(results,columns=metric_names,index=['symChecker','BehaviorChecker','Synthetic','symChecker','BehaviorChecker','Synthetic'])
res.to_csv('metrics1-1.csv')

# plot_PR(y_true_sym,y_sym)
# plot_PR(y_true_bhv,y_bhv)
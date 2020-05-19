import os
import pandas as pd
import numpy as np
from datetime import datetime

nponzi = os.path.join('feature','nponzi_feature_raw.csv')
r_file = os.path.join('database','nponzi_time_in.out')
record = os.path.join('database','nponzi_in_record')
valid = [3, 11, 34, 38, 43, 44, 47, 48, 49, 50, 52, 53, 64, 70, 73, 74, 76, 91, 98, 103, 105, 106, 107, 109, 111, 114, 118, 126, 127, 136, 147, 149, 156, 157, 160, 161, 163, 164, 168, 171, 172, 175, 181, 185, 186, 189, 192, 199, 206, 207, 208, 209, 211, 219, 223, 225, 228, 231, 232, 234, 235, 240, 242, 245,252, 255, 260, 265, 266, 268, 274, 278, 291, 293, 301, 307, 311, 313, 315, 317, 319, 323, 328, 331, 342, 344, 346, 351, 352, 353, 354, 358, 370, 375, 376, 380, 382, 397, 398, 412, 415, 419, 420, 424, 430, 432, 435, 436, 438, 442, 450, 451, 453, 460, 463, 466, 467, 468, 478, 482, 487, 489, 491, 492, 496, 498]
name_feature = ['index','ponzi','time_in','val_in','time_out','val_out']

def deal_time():
    numbers = pd.read_csv(record).values
    print('-----Dealing with '+r_file+' -----')
    timestamps = []
    with open(r_file,'r',encoding='utf-8') as f:
        line = f.readline()
        times = []
        num = 0
        index = 0
        while(line!='EOF'):
            line = line.strip()
            if line == '':
                line = f.readline()
                continue
            if line[0] =='2':
                number = numbers[index][0]
                time = line[:-3]
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                time = time.timestamp()
                if num < number:
                    num = num + 1
                    times.append(time)
                    times = [min(times), max(times)]
                else:
                    num = 0
                    index = index + 1
                    if number==0:
                        timestamps.append('0')
                    else:
                        timestamps.append(str(times))
                    continue
            line = f.readline()
    timestamps.append(str(times))

    print('-----Writing '+nponzi+'.-----')
    timestamps = pd.DataFrame(timestamps,columns=['time_in'])
    raw_feature = pd.read_csv(nponzi)
    time_out = raw_feature['time_out']
    timestamps['time_out'] = time_out
    timestamps.to_csv(nponzi,index=False)
    print('-----Done------')

def deal_val_csv(file, name):
    print('-----Dealing with '+file+'.-----')
    values = []
    with open(file) as f:
        line = f.readline()
        while(True):
            line = f.readline()
            if line=='':
                break
            value = line.split('[')[1]
            value = value.split(']')[0]
            index = line.split(',')[0]
            values.append([index,'['+value+']'])
    
    values = pd.DataFrame(values,columns=['index',name])
    return values


def deal_value():
    val_in_file = os.path.join('feature','nponzi_feature_in.csv')
    val_out_file = os.path.join('feature','nponzi_feature_out.csv')
    
    val_in = deal_val_csv(val_in_file,'val_in')
    val_out = deal_val_csv(val_out_file,'val_out')
    values = pd.merge(val_in,val_out,on='index',how='right')

    times = pd.read_csv(nponzi)
    values['time_in'] = times['time_in']
    values['time_out'] = times['time_out']
    ponzi = ['0'] * values.shape[0]
    values['ponzi'] = ponzi

    print('-----Writing '+nponzi+'.-----')
    values.to_csv(nponzi+'.new',index=False)
    print('-----Done------')

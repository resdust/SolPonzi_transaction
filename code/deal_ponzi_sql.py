import os
import pandas as pd

names_feature = ['index','ponzi','time_in','val_in','time_out','val_out']
names_transaction = ['index','ponzi','to_address','from_address','timestamp','value']

"""
First, excute sql_query.val_sql() to get sql command files for 
queries of transactions.
Then excure the query files on database server to get out files.
"""
def deal_out(file,ponzi): 
    print('-----Dealing with '+file+' -----')
    address = pd.read_csv(ponzi_address).values
    transactions = []

    with open(file,'r',encoding='utf-8') as f:
        line = f.readline()
        index = 0
        while(line!='EOF'):
            line = line.strip()
            data = []
            if line == '':
                line = f.readline()
                continue

            if line[0] == '(':
                index = index+1

            if line[0] =='\\':
                attributes = line.split('|')
                for i in range(len(attributes)):
                    attributes[i] = attributes[i].strip()
                data = [index, ponzi, attributes[9], attributes[2], 
                attributes[8], attributes[12]]
                transactions.append(data)
            line = f.readline()

    df = pd.DataFrame(data=transactions, columns=names_transaction)
    df.to_csv(os.path.join('database','ponzi_transaction_out.csv'),index=False)
    print('-----Done------')

def deal_in(file,ponzi): 
    print('-----Dealing with '+file+' -----')
    transactions = []
    block_hash = []

    with open(file,'r',encoding='utf-8') as f:
        index = 0
        line = f.readline()
        while(line!='EOF'):
            line = line.strip()
            if line == '':
                line = f.readline()
                continue
    
            if line[0] == '(':
                index = index + 1

            data = []
            if line[0] =='\\':
                attributes = line.split('|')
                for i in range(len(attributes)):
                    attributes[i] = attributes[i].strip()
                data = [index, ponzi, attributes[1], attributes[0], '', attributes[3]]
                block_hash.append(attributes[2])
                transactions.append(data)
            line = f.readline()

    df = pd.DataFrame(data=transactions, columns=names_transaction)
    df.to_csv(os.path.join('database','nponzi_transaction_in.csv'),index=False)
    print('-----Done------')
    '''
    Cause the external transaction does not have a timestamp clumns in its table,
    record block hashes dumping into file, 
    then pull timestamp of blocks as the timestamp of transaction
    '''
    hashes = pd.DataFrame(data=block_hash,columns=['block_hash'])
    hashes.to_csv(os.path.join('database','nponzi_hashes_in.csv'),index=False)
    print('Have recorded transaction ')

ponzi_val_in = os.path.join('database','ponzi_val_in.out')
ponzi_val_out = os.path.join('database','ponzi_val_out.out')
ponzi_address = os.path.join('database','ponzi.csv')

# deal_out(ponzi_val_out,'1')
# deal_in(ponzi_val_in,'1')
# deal_out(os.path.join('database','nponzi_val_out.out'),'0')
deal_in(os.path.join('database','nponzi_val_in.out'),'0')

"""
After recording internal transaction hashes, excute sql_query.timestamp_sql() 
to get a sql command file for queries.
Then excure the query file on database server.
"""

def deal_in_timestamp(w_file, r_file):
    print('-----Dealing with '+r_file+' -----')
    transactions = pd.read_csv(w_file)
    timestamps = []

    with open(r_file,'r',encoding='utf-8') as f:
        line = f.readline()
        while(line!='EOF'):
            line = line.strip()
            if line == '':
                line = f.readline()
                continue

            if line[0] =='2':
                timestamps.append(line)
            line = f.readline()

    j = 0
    for i in range(transactions.shape[0]):
        if transactions['to_address'][i]:
            # not empty
            transactions.loc[i,'timestamp'] = timestamps[j]
            j = j+1
    transactions.to_csv(os.path.join('sm_database','ponzi_transaction_in.csv'),index=False)
    print('-----Done------')

ponzi_timestamp_in = os.path.join('sm_database','ponzi_timestamp_in.out')
# deal_in_timestamp(os.path.join('sm_database','ponzi_transaction_in.csv'), ponzi_timestamp_in)

def deal_out_timestamp(w_file, r_file):
    print('-----Dealing with '+r_file+' -----')
    transactions = pd.read_csv(w_file)
    timestamps = []

def sequence(df, tp):
    from datetime import datetime

    ins = df
    val_ins = {}
    time_ins = {}
    val_in = []
    time_in = []
    addr = ins[tp][0]
    index = ins['index'][0]
    for i in range(ins.shape[0]):
        value = ins['value'][i]
        time = ins['timestamp'][i][:-3]
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        time = time.timestamp()

        if addr == ins[tp][i]:
            val_in.append(value)
            time_in.append(time)
        else:
            val_ins[index]=val_in
            time_ins[index]=time_in
            val_in = [value]
            time_in = [time]
        addr = ins[tp][i]
        index = ins['index'][i]

    return val_ins, time_ins

def deal_feature(file_in, file_out, file_feature, ponzi):
    print('-----Dealing with features-----')
    contracts = []

    ins = pd.read_csv(file_in,encoding='utf-8')
    outs = pd.read_csv(file_out, encoding='utf-8')

    val_ins, time_ins = sequence(ins, 'to_address')
    val_outs, time_outs = sequence(outs, 'from_address')

    for i in range(184):
        contract = [i, ponzi]
        if i in val_ins.keys():
            contract.append(time_ins[i])
            contract.append(val_ins[i])
        else:
            contract.append('')
            contract.append('')
        if i in val_outs.keys():
            contract.append(time_outs[i])
            contract.append(val_outs[i])
        else:
            contract.append('')
            contract.append('')
        contracts.append(contract)
    df = pd.DataFrame(data=contracts,columns=names_feature)
    df.to_csv(file_feature, index=False)
    print('-----Have generated '+file_feature+'.-----')

transaction_in = r'sm_database\ponzi_transaction_in.csv'
transaction_out = r'sm_database\ponzi_transaction_out.csv'

# deal_feature(transaction_in, transaction_out,
#     os.path.join('feature_data','ponzi_feature_raw.csv'), '1')
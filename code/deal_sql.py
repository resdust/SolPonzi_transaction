import os,sys
import pandas as pd
import color
import sql_query as sq

names_feature = ['address','time_in','val_in','time_out','val_out']
names_transaction = ['address','timestamp','value']

"""
First, excute sql_query.val_sql() to get sql command files for 
queries of transactions.
Then excure the query files on database server to get out files.
"""

def readAddr(addr):
    import pandas as pd
    '''
    with open(addr)as f:
        addrs = []
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        if line[0]=='\\':
            a = line
            addrs.append(a)
    '''
    addrs = pd.read_csv(addr,header=-1)
    addrs = addrs.values
    print('read addrs number:',len(addrs))
    return addrs

def deal_out(addr_file,in_file,to_file): 
    color.pInfo('Dealing with '+in_file)
    os.system('echo \"EOF\" >> '+in_file)

    address = readAddr(addr_file)
    transactions = []

    with open(in_file,'r',encoding='utf-8') as f:
        line = f.readline().strip()
        index = 0
        while(line!='EOF'):
            data = []
            if line == '':
                line = f.readline().strip()
                continue

            if line[0] == '(':
                index = index+1

            if line[0] =='2':
                attributes = line.split('|')
                for i in range(len(attributes)):
                    attributes[i] = attributes[i].strip()
                data = [address[index], attributes[0], attributes[1]]
                transactions.append(data)
            line = f.readline().strip()

    color.pInfo('collected '+str(len(transactions))+' transactions.')
    df = pd.DataFrame(data=transactions, columns=names_transaction)
    df.to_csv(to_file,index=False)
    color.pDone('Done')

def deal_in(addr_file, in_file, to_file): 
    color.pInfo('Dealing with '+in_file)
    os.system('echo \"EOF\" >> '+in_file)

    address = readAddr(addr_file)
    transactions = []
    block_hash = []

    with open(in_file,'r',encoding='utf-8') as f:
        index = 0
        line = f.readline().strip()
        while(line!='EOF'):
            if line == '':
                line = f.readline().strip()
                continue
    
            if line[0] == '(':
                index = index + 1

            data = []
            if line[0] =='\\':
                attributes = line.split('|')
                for i in range(len(attributes)):
                    attributes[i] = attributes[i].strip()
                try:
                    data = [address[index], '',attributes[1]]
                    block_hash.append(attributes[0])
                    transactions.append(data)
                except:
                    color.pError('out of index')
                    print('index',index)
                    print('attribute',attributes)
                    break
                    
            line = f.readline().strip()

    df = pd.DataFrame(data=transactions, columns=names_transaction)
    df.to_csv(to_file,index=False)
    color.pDone('Done')
    '''
    Cause the external transaction does not have a timestamp clumns in its table,
    record block hashes, 
    then pull timestamp of the block as the timestamp of transactions
    '''
    
    return block_hash



"""
After recording internal transaction hashes, excute sql_query.timestamp_sql() 
to get a sql command file for queries.
Then excure the query file on database server.
"""

def deal_in_timestamp(txn_file, time_file):
    color.pInfo('Dealing with '+time_file)
    os.system('echo \"EOF\" >> '+time_file)

    transactions = pd.read_csv(txn_file, low_memory=False)
    timestamps = []
    num = 0

    with open(time_file,'r',encoding='utf-8') as f:
        line = f.readline().strip()
        while(line!='EOF'):
            if line == '':
                line = f.readline().strip()
                continue

            if line[0] =='2':
                timestamps.append(line)
                num = num+1
                if num%1000000==0:
                    color.pDone('dealed '+str(num)+' timestamps')
            line = f.readline().strip()
    color.pInfo('adding timestamps to transaction')
    j = 0
    last = transactions['address'][0]
    for i in range(transactions.shape[0]):
        if transactions['address'][i]:
            # not empty
            transactions.loc[i,'timestamp'] = timestamps[j]
            if transactions['address'][i]!=last:
                color.pInfo(transactions['address'][i]+' transaction:'+str(i))
            
            last = transactions['address'][i]
            j = j+1
    color.pInfo('writing to '+txn_file+' .')
    transactions.to_csv(txn_file,index=False)
    color.pDone('Done')

def sequence(df):
    from datetime import datetime

    ins = df
    val_ins = {}
    time_ins = {}
    val_in = []
    time_in = []
    addr_ins = []
    addrs = ins['address'].values
    addrs = [eval(x)[0] for x in addrs]
    addr = addrs[0]

    for i in range(ins.shape[0]):
        value = ins['value'][i]
        time = ins['timestamp'][i][:-3]
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        time = time.timestamp()

        if addr == addrs[i]:
            val_in.append(value)
            time_in.append(time)
        else:
            val_ins[i]=str(val_in)
            time_ins[i]=str(time_in)
            val_in = [value]
            time_in = [time]
            addr_ins.append(addr)
        addr = addrs[i]
    val_ins = list(val_ins.values())
    time_ins = list(time_ins.values())
    
    return addr_ins,val_ins, time_ins

def deal_feature(file_in, file_out, file_data, ponzi=None):
    color.pInfo('Dealing with features')
    contracts = []

    ins = pd.read_csv(file_in,encoding='utf-8')
    outs = pd.read_csv(file_out, encoding='utf-8')

    addr_in, val_ins, time_ins = sequence(ins)
    addr_out, val_outs, time_outs = sequence(outs)
    
    ins = [[addr_in[i],val_ins[i],time_ins[i]] for i in range(len(addr_in))]
    outs = [[addr_out[i],val_outs[i],time_outs[i]] for i in range(len(addr_out))]
    
    df_in = pd.DataFrame(ins, columns=['address','val_in','time_in'])
    df_out = pd.DataFrame(outs, columns=['address','val_out','time_out'])

    # for i in range(max(ins.shape[0],outs.shape[0])):
    #     contract = [i, ponzi] if ponzi else [i]
    #     if i in val_ins.keys():
    #         contract.append(time_ins[i])
    #         contract.append(val_ins[i])
    #     else:
    #         contract.append('')
    #         contract.append('')
    #     if i in val_outs.keys():
    #         contract.append(time_outs[i])
    #         contract.append(val_outs[i])
    #     else:
    #         contract.append('')
    #         contract.append('')
    #     contracts.append(contract)
    df = pd.concat([df_in,df_out],join='outer',axis=1)
    df.to_csv(file_data, index=False)
    color.pDone('Have generated '+file_data+'.')

if __name__=='__main__':
    ponzi_val_in = os.path.join('database','ponzi_val_in.out')
    ponzi_val_out = os.path.join('database','ponzi_val_out.out')
    ponzi_address = os.path.join('database','ponzi.csv')

    # deal_out(ponzi_val_out,'1')
    # deal_in(ponzi_val_in,'1')
    # deal_out(os.path.join('database','nponzi_val_out.out'),'0')
    deal_in(os.path.join('database','nponzi_val_in.out'),'0')

    ponzi_timestamp_in = os.path.join('database','ponzi_timestamp_in.out')
    # deal_in_timestamp(os.path.join('database','ponzi_transaction_in.csv'), ponzi_timestamp_in)

    transaction_in = r'sm_database\ponzi_transaction_in.csv'
    transaction_out = r'sm_database\ponzi_transaction_out.csv'

    # deal_feature(transaction_in, transaction_out,
    #     os.path.join('feature_data','ponzi_feature_raw.csv'), '1')

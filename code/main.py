# !/usr/bin/python3

"""
Run 'python3 main.py' to select contract addresses from table 'code',
which have published their source code. 
This program then automatically sends query to postgresql server for 
necessary information,
and transfers the information into feature for machine learning test.
"""

import os
import sys
import pandas as pd
import pexpect
import deal_sql

N = 1000 # query N instances each time

def examLog(log_file):
    from pathlib import Path

    path = Path(log_file)
    if not path.exists():
        with open(log_file,'w') as f:
            f.write(getTime())
            f.write('\n0\n')

def writeLog(log_file,line):
    with open(log_file,'a') as f:
        f.write(getTime())
        f.write('\n'+str(line)+'\n')

# return last line in string type
def fetchLog(log_file):
    with open(log_file,'r') as f:
        log = f.readlines()
        num = log[-1].strip()
    
    return num

def getTime():
    import time

    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def connectPSQL(psql):
    import getpass

    p = pexpect.spawn(psql)

    p.expect('gby:') 
    pwd = getpass.getpass('Password:')
    p.sendline(pwd)
    p.expect('#')
    print('Successfully connected to PostgreSQL!')

    return p

# collect address of contracts publishing source code and having transactions
def collectAddr(p, n=N, timeout=120):
    log_file = os.path.join('log','collect.log')
    examLog(log_file)
    last = fetchLog(log_file)
    new = int(last)+N

    # os.makedirs('test_addr')
    out_file = os.path.join('result','addr_'+last+'.out')
    print(out_file)
    p.sendline('\o ' + out_file)
    p.expect('#')

    query='SELECT address FROM code WHERE address IN \
    (SELECT to_address from external_transaction WHERE value!=\'0\' ORDER BY number DESC limit \
    '+str(N)+' OFFSET '+str(last)+') ORDER BY number DESC;'
    p.sendline(query)
    print('Excuting query \''+query+'\', raising TimeOut \
        exception in '+str(timeout)+' sec.')
    p.expect('#',timeout=timeout)
    print('Done query.')

    with open(out_file) as f:
        out = f.readlines()
    try:
        out = out[-2]
    except:
        print('Failed to write the results')
        p.close()
        sys.exit(1)

    print('Collected address '+out+'\nWritten in '+out_file+' .')
    writeLog(log_file,new)

def collectTxnIn(p, addr):
    import sql_query as sq

    print('Collecting transactions into contract')
    query_in = [
        'select block_hash,value from external_transaction where to_address=\'',
        '\' and value!=\'0\';\r'
        ]
    name = os.path.basename(addr).split('.')[0]
    print('address file name: '+name)

    # write query file for block_hash and txn value
    sql_file = os.path.join('sql',name+'in.sql')
    sq.val_sql(addr, sql_file, query_in)
    
    # send command to sql process
    out_file = os.path.join('result',name+'_in.out')
    p.sendline('\o '+out_file)
    p.sendline('\i '+sql_file)

    # write query file for timestamp
    txn_file = os.path.join('result',name+'_in.csv')
    hash_sql = deal_sql.deal_in(addr, out_file, txn_file)

    # send command to sql process
    time_file = os.path.join('result',name+'_time.out')
    p.sendline('\o '+time_file)
    p.sendline('\i '+hash_sql)

    # collect the query result into txn features
    txn_file = os.path.join('result',addr.split('.')[0]+'_in.csv')
    deal_sql.deal_in_timestamp(txn_file, time_file, txn_file)

    return txn_file

def collectTxnOut(p, addr):
    import sql_query as sq

    print('Collecting transactions out of contract')
    query_out = [
        'select timestamp, value from internal_transaction where from_address=\'\\',
        '\' and value!=\'0\';\r'
    ]
    name = os.path.basename(addr).split('.')[0]
    print('address file name: '+name)

    # write query file for block_hash and txn value
    sql_file = os.path.join('sql',name+'out.sql')
    sq.val_sql(addr, sql_file, query_out)

    # send command to sql process
    out_file = os.path.join('result',name+'_out.out')
    p.sendline('\o '+out_file)
    p.sendline('\i '+sql_file)

    # collect the query result into txn features
    txn_file = os.path.join('result',name+'_out.csv')
    deal_sql.deal_out(addr, out_file, txn_file)

    return txn_file
      	
if __name__=='__main__':
    args = sys.argv
    try:
        Round = args[1]
    except:
        print('usage: python main.py [Round]')
        sys.exit(1)

    # os.makedirs('log')
    # os.makedirs('sql')

    psql = 'psql --host 192.168.1.2 -U gby ethereum'

    # collect addresses
    # p = connectPSQL(psql)
    # for i in range(int(Round)):
    #     print('Collecting round ', i)
    #     collectAddr(p)
    # p.sendline('\q')
    # p.close()

    # collect val and time sequence from addresses
    p = connectPSQL(psql)

    dirPath = 'test_addr'
    addrs = os.listdir(dirPath)
    for addr in addrs:
        if addr[0]!='d':
            full_path = os.path.join(dirPath,addr)
            feature = 'test_'+addr.split('.')[0].split('_')[1]+'.csv'
            in_csv = collectTxnIn(p,full_path)
            out_csv = collectTxnOut(p,full_path)
            deal_sql.deal_feature(in_csv, out_csv, feature)
            os.rename(full_path,os.path.join(dirPath,'done-'+addr))

    p.close()

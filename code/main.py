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
    out_file = os.path.join('test_addr','addr_'+last+'.out')
    print(out_file)
    p.sendline('\o ' + out_file)
    p.expect('#')

    query='SELECT address FROM code WHERE address IN \
    (SELECT to_address from external_transaction ORDER BY number DESC limit \
    '+str(N)+' OFFSET '+str(last)+') ORDER BY number DESC;'
    p.sendline(query)
    print('Excuting query \''+query+'\', raising TimeOut \
        exception in '+timeout+' sec.')
    p.expect('#',timeout=timeout)
    print('Done query.')

    with open(out_file) as f:
        out = f.readlines()
    try:
        out = out[-2]
    except:
        print('Failed to write the results')
        p.kill(0)
        sys.exit(1)

    print('Collected address '+out+'. Written in '+out_file+' .')
    writeLog(log_file,new)

def collectTxnIn(p, addr):
    import sql_query as sq

    print('Collecting transaction in')
    query = [
        'select to_address,block_hash,value from external_transaction where to_address=\'',
        '\';\r'
        ]

    sql_file = os.path.join('sql',addr.split('.')[0]+'.sql')
    with open(sql_file,'w') as f:
        pass
    
    with open(addr)as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line[0]=='\\':
                a = line
                q = query[0]+a+query[1]
                with open(sql_file,'a') as f:
                    f.write(q)

def collectTxnOut():
    print('Collecting transaction out')
      	
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
    p = connectPSQL(psql)
    p = None
    for i in range(int(Round)):
        print('Collecting round ', i)
        collectAddr(p)
    p.sendline('\q')
    p.kill(0)

    # collect val and time sequence from addresses
    p = connectPSQL(psql)
    dirPath = 'test_addr'
    addrs = os.listdir(dirPath)
    for addr in addrs:
        if addr[0]!='d':
            full_path = os.path.join(dirPath,addr)
            collectTxnIn(full_path)
            collectTxnOut(full_path)
            os.rename(full_path,os.path.join(dirPath,'done-'+addr))

    p.close()

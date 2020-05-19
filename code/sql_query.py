import pandas as pd
import os
import color

query_out = [
    'select timestamp, value from internal_transaction where from_address=\'\\',
    '\' and value!=\'0\';\r'
]

query_in = [
    'select block_hash,value from external_transaction where to_address=\'',
    '\' and value!=\'0\';\r'
]

def readAddr(addr):
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
    return addrs

def val_sql(addr_file, file,query):
    ponzi_addr = readAddr(addr_file)
    with open(file,'w',encoding='utf-8') as f:
        for data in ponzi_addr:
            sentence = query[0]+data+query[1]
            f.write(sentence)
    color.pDone('Have generated '+file+'.')

def timestamp_sql(in_file, file):
    f = in_file
    hashes = pd.read_csv(f).values
    with open(file,'w',encoding='utf-8') as f:
        for data in hashes:
            data = data[0][1:]
            sentence = 'select timestamp from block where hash=\'\\'+data+'\';\r'
            f.write(sentence)
    color.pDone('Have generated '+file+'.')

if __name__=='__main__':
    # val_sql(os.path.join('database','add_ponzi.csv'),'ponzi_val_out.sql',query_out)
    # val_sql(os.path.join('database','add_ponzi.csv'),'ponzi_val_in.sql',query_in)

    val_sql(os.path.join('database','add_nponzi_code.csv'),'nponzi_val_out.sql',query_out)
    val_sql(os.path.join('database','add_nponzi_code.csv'), 'nponzi_val_in.sql', query_in)
        
    timestamp_sql(os.path.join('database','ponzi_hashes_in.csv'),'ponzi_timestamp_in.sql')
    timestamp_sql(os.path.join('database','nponzi_hashes_in.csv'),'nponzi_timstamp_in.sql')

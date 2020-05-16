import pandas as pd
import os

def val_sql(in_file, file,query):
    addr = in_file
    ponzi_addr = pd.read_csv(addr)
    ponzi_addr = ponzi_addr.values
    with open(file,'w',encoding='utf-8') as f:
        for data in ponzi_addr:
            a = data[0]
            a = a[2:]
            sentence = query+a+'\';\r'
            f.write(sentence)
    print('---Have generated '+file+'.---')

query_out = 'select * from internal_transaction where from_address=\'\\'
query_in = 'select * from external_transaction where to_address=\'\\'

# val_sql(os.path.join('database','add_ponzi.csv'),'ponzi_val_out.sql',query_out)
# val_sql(os.path.join('database','add_ponzi.csv'),'ponzi_val_in.sql',query_in)

val_sql(os.path.join('database','add_nponzi_code.csv'),'nponzi_val_out.sql',query_out)
val_sql(os.path.join('database','add_nponzi_code.csv'), 'nponzi_val_in.sql', query_in)

def timestamp_sql(in_file, file):
    f = in_file
    hashes = pd.read_csv(f).values
    with open(file,'w',encoding='utf-8') as f:
        for data in hashes:
            data = data[0][1:]
            sentence = 'select timestamp from block where hash=\'\\'+data+'\';\r'
            f.write(sentence)
    print('---Have generated '+file+'.---')

# timestamp_sql(os.path.join('database','ponzi_hashes_in.csv'),'ponzi_timestamp_in.sql')
# timestamp_sql(os.path.join('database','nponzi_hashes_in.csv'),'nponzi_timstamp_in.sql')
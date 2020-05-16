# Dr.SolPonzi
 
This responsity is built for classifying the smart contract in Ethereum by analysing transaction behaviors. The whole classification work is designed for a competition.
All the transaction data are collected from a PostgreSQL database server. 

## Feature
## 特征

```python
ft_names = [
        'ponzi', # ponzi:'1', normal:'0'
        'nbr_tx_in', # 向合约转账交易总次数
        'nbr_tx_out', # 合约分红交易总次数
        'Tot_in', # 向合约转账的总金额
        'Tot_out', # 合约分红的总金额
        'mean_in', # 向合约转账的平均金额
        'mean_out', # 合约分红的平均金额
        'sdev_in', # 向合约转账金额的标准方差
        'sdev_out', # 合约分红金额的标准方差
        'gini_in', # 向合约转账金额的基尼系数
        'gini_out', # 合约分红金额的基尼系数
        'avg_time_btw_tx', # 平均多长时间有一笔交易
        'lifetime', # 合约生存周期
    ]
```

要得到以上特征，需要合约标签（`ponzi`）、向合约转账的金额列表(`val_in`)、合约分红的金额列表(`val_out`)、合约生存周期(`lifetime=max(time_in+time_out)-min(timein+time_out)`)。

## 数据处理

### 1 addr 庞氏合约与正常合约地址列表

- [庞氏合约地址](https://github.com/blockchain-unica/ethereum-ponzi/blob/master/ponzi-addresses.csv) `add_ponzi.csv`

- 正常合约：从公开代码的正常合约中随机抽取600个有转账交易的合约地址作为对比。

```sql
ethereum=# \o add_nponzi_code.out
ethereum=# select address from code where address in ( select from_address from internal_transaction order by random() limit 1000) limit 600;
```

​		python写入`add_nponzi_code.csv`

```python
with open('add_nponzi_code.out') as f:
	addr = f.readlines()
	addr = addr[2:-2]
    
for i in range(len(addr)):
    addr[i] = addr[i].strip()+'\n'
    
with open('add_nponzi_code.csv','w') as f:
    f.writelines(addr)
```

浙大数据库的部分表如下：

```
 public | ac2_external_target          | table | tch
 public | ac_target                    | table | gpadmin
 public | balance                      | table | gpadmin
 public | block                        | table | gpadmin
 public | code                         | table | gpadmin
 public | code_temp                    | table | gpadmin
 public | create_account               | table | gpadmin
 public | critical_keys                | table | dmc
 public | erc20_transfer               | table | gpadmin
 public | external_transaction         | table | gpadmin
 public | internal_transaction         | table | gpadmin
 public | nonce                        | table | gpadmin
 public | price                        | table | dmc
 public | private_key                  | table | gpadmin
 public | reentrancy                   | table | gpadmin
 public | storage                      | table | dmc
 public | suicide                      | table | gpadmin
 public | transaction_log              | table | gpadmin
```

### 2 val_in 向合约转账的金额列表

In table `external_transaction`，找到to_address为合约地址的交易，得到所有向合约转账的交易记录。表中列名如下例所示：

| 0    | block_hash     | \x5c45551ca7f85df5183bdcb970aa495bb092c50d109772e1243caa0521f838b9 |      |      |
| ---- | -------------- | ------------------------------------------------------------ | ---- | ---- |
| 1    | call_function  | \x                                                           |      |      |
| 2    | call_parameter | {}                                                           |      |      |
| 3    | con_address    | \x                                                           |      |      |
| 4    | cum_gas_used   | 425907                                                       |      |      |
| 5    | from_address   | \x5c119783b3e8b2802fb154257830a95f0efd5c26                   |      |      |
| 6    | gas_limit      | 294907                                                       |      |      |
| 7    | gas_price      | 20000000000                                                  |      |      |
| 8    | gas_used       | 194907                                                       |      |      |
| 9    | hash           | \x2b20d7c3ea9e3b9432896cf1f4c8f951e534ece482ea009401994e3f50119a58 |      |      |
| 10   | int_txn_count  | 4                                                            |      |      |
| 11   | nonce          | 31                                                           |      |      |
| 12   | number         | 1291829                                                      |      |      |
| 13   | status         | t                                                            |      |      |
| 14   | to_address     | \xba69e7c96e9541863f009e713caf26d4ad2241a0                   |      |      |
| 15   | txn_index      | 11                                                           |      |      |
| 16   | value          | 100000000000000000                                           |      |      |

```python
with open('add_nponzi_code.csv') as f:
	addr = f.readlines()

with open('nponzi_in.sql','w') as f:
    for a in addr:
            f.write('select to_address,block_hash,value from external_transaction where to_address=\''+a.strip()+'\';\r')
```

time_in

```python
with open('nponzi_time.sql','w') as f:
    for a in addr:
            f.write('select max(timestamp),min(timestamp) from external_transaction where to_address=\''+a.strip()+'\';\r')

```

### 3 val_out 合约分红的金额列表

in table `internal_transaction`、

| 0    | call_function   | \x                                                           |
| ---- | --------------- | ------------------------------------------------------------ |
| 1    | call_parameter  |                                                              |
| 2    | from_address    | \xba69e7c96e9541863f009e713caf26d4ad2241a0                   |
| 3    | gas_limit       | 2300                                                         |
| 4    | int_txn_index   | 0                                                            |
| 5    | number          | 1291829                                                      |
| 6    | output          | \x                                                           |
| 7    | parent_txn_hash | \x2b20d7c3ea9e3b9432896cf1f4c8f951e534ece482ea009401994e3f50119a58 |
| 8    | timestamp       | 2016-04-07 08:07:51+00                                       |
| 9    | to_address      | \xfcb8d083e3a5986c2eeea6edec7def8b7a4cbbae                   |
| 10   | txn_index       | 11                                                           |
| 11   | type            | 241                                                          |
| 12   | value           | 1000000000000000                                             |

```python
with open('nponzi_out.sql','w') as f:
    for a in addr:
        f.write('select value from internal_transaction where from_address=\'' + a.strip() + '\';\r')
```

time_out

```python
with open('nponzi_time_in.sql','a') as f:
    f.write('select timestamp from block where hash=\''+hash+'\';\r')
```

### 4 lifetime

使用time_in和time_out序列来判断，距离最远的两个时刻间隔即为lifetime

由于external表中没有lifetime字段，查找block_hash获得交易时间

```
                 Table "public.block"
   Column   |            Type             | Modifiers 
------------+-----------------------------+-----------
 hash       | bytea                       | 
 number     | integer                     | not null
 timestamp  | timestamp(0) with time zone | 

```

## 训练集机器学习结果

使用决策树算法J48，十折交叉验证，ponzi 156个，nponzi 126个，正确率93%

![image-20200515201517103](C:\Users\14415\AppData\Roaming\Typora\typora-user-images\image-20200515201517103.png)

```
J48 pruned tree
------------------
lifetime <= 88073120
|   nbr_tx_in <= 0: 0 (18.0)
|   nbr_tx_in > 0
|   |   lifetime <= 4634216: 1 (96.0)
|   |   lifetime > 4634216
|   |   |   sdev_in <= 178112740491363232
|   |   |   |   Tot_in <= 524363083743762050: 1 (5.0)
|   |   |   |   Tot_in > 524363083743762050: 0 (8.0)
|   |   |   sdev_in > 178112740491363232
|   |   |   |   sdev_out <= 73531197031330220000: 1 (50.0/2.0)
|   |   |   |   sdev_out > 73531197031330220000: 0 (3.0/1.0)
lifetime > 88073120
|   lifetime <= 91143919: 0 (96.0/2.0)
|   lifetime > 91143919
|   |   Tot_in <= 30023101111000000: 0 (2.0)
|   |   Tot_in > 30023101111000000: 1 (4.0)

Number of Leaves  : 	9

Size of the tree : 	17


Time taken to build model: 0.01 seconds

=== Stratified cross-validation ===
=== Summary ===

Correctly Classified Instances         263               93.2624 %
Incorrectly Classified Instances        19                6.7376 %
Kappa statistic                          0.8638
Mean absolute error                      0.0811
Root mean squared error                  0.2506
Relative absolute error                 16.3945 %
Root relative squared error             50.4095 %
Total Number of Instances              282     

=== Detailed Accuracy By Class ===

                 TP Rate  FP Rate  Precision  Recall   F-Measure  MCC      ROC Area  PRC Area  Class
                 0.929    0.064    0.921      0.929    0.925      0.864    0.946     0.890     0
                 0.936    0.071    0.942      0.936    0.939      0.864    0.946     0.958     1
Weighted Avg.    0.933    0.068    0.933      0.933    0.933      0.864    0.946     0.927     

=== Confusion Matrix ===

   a   b   <-- classified as
 117   9 |   a = 0 (nponzi)
  10 146 |   b = 1 (ponzi)
```

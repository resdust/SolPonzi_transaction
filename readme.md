# Dr.SolPonzi

> This responsity is built for classifying the smart contract in Ethereum by analysing transaction behaviors. The whole classification work is designed for a competition.
> All the transaction data are collected from a PostgreSQL database server. 
>
> 通过分析链上交易行为来鉴别Ethereum中的庞氏智能合约。这个项目仅是比赛项目的一部分工作。
> 所有的交易数据来自某高校课题组提供的PostgreSQL数据库服务器。

由于机器学习提取合约的行为特征需要大量的交易数据，我们依托于高校实验室的PostgreSQL数据库服务器，编写了从合约地址提取交易数据并生成行为特征数据的自动化脚本。脚本的全部代码上传到GitHub开源代码平台中，可以通过浏览器访问https://github.com/resdust/SolPonzi_transaction。脚本设计流程如下图所示

![](F:\worktask\信安作品赛\SolPonzi_transaction\数据收集流程.png)

首先利用已公开的庞氏合约数据集和相同数量随机选取的Dapp合约地址作为训练集，使用本工程生成带标签的特征文件后输入到WEKA机器学习集成工具中。选用随机森林算法训练模型，得到分类模型。

后续使用相同的步骤生成测试集的未标签特征文件，输入到WEKA中，使用已训练好的分类模型输出判断结果。

## 使用方法与运行效果

目前只适用于特定的以太坊数据库服务器。

自动化脚本使用python3编写，可以在PostgreSQL数据库服务器上通过一行命令直接运行，输入数据为csv格式的合约地址集，输出数据为csv格式的特征数据集。脚本运行过程中记录服务器查询命令的日志文件，方便追踪错误，同时适当输出运行中产生的阶段日志。生成71个随机合约的行为特征的整体运行效果如下图所示：

![](F:\worktask\信安作品赛\SolPonzi_transaction\自动化查询工具运行效果.png)

运行命令：

```shell
pip install scipy,sklearn,matplotlib
python code/main.py
```

## Feature 特征

| 特征名称        | 含义                                     | 类型         |
| --------------- | ---------------------------------------- | ------------ |
| ponzi           | 是否为庞氏合约的标签，庞氏：1，normal：0 | nominal{0,1} |
| nbr_tx_in       | 向合约转账交易总次数                     | numerical    |
| nbr_tx_out      | 合约向外转账总次数                       | numerical    |
| Tot_in          | 向合约转账的总金额                       | numerical    |
| Tot_out         | 合约向外转账的总金额                     | numerical    |
| mean_in         | 向合约转账的平均金额                     | numerical    |
| mean_out        | 合约向外转账的平均金额                   | numerical    |
| sdev_in         | 向合约转账金额的标准方差                 | numerical    |
| sdev_out        | 合约向外转账金额的标准方差               | numerical    |
| gini_in         | 向合约转账金额的基尼系数                 | numerical    |
| gini_out        | 合约向外转账金额的基尼系数               | numerical    |
| avg_time_btw_tx | 平均多长时间有一笔交易                   | numerical    |
| lifetime        | 合约生存周期                             | numerical    |

要得到以上特征，需要合约标签（`ponzi`）、向合约转账的金额列表(`val_in`)、合约分红的金额列表(`val_out`)、合约生存周期(`lifetime=max(time_in+time_out)-min(timein+time_out)`)。

## Data Processing 数据处理

### 1 addr 庞氏合约与正常合约地址列表

- [庞氏合约地址](https://github.com/blockchain-unica/ethereum-ponzi/blob/master/ponzi-addresses.csv) `add_ponzi.csv`

- 正常合约：从公开代码的正常合约中随机抽取600个有转账交易的合约地址。

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
query_in = [
    'select block_hash,value from external_transaction where to_address=\'',
    '\' and value!=\'0\';'
]
with open('add_nponzi_code.csv') as f:
	addr = f.readlines()

with open('nponzi_in.sql','w') as f:
    for a in addr:
            f.write(query_in[0]+a.strip()+query_in[1])
```

time_in

```python
p=connectSQL()
hashes = in_hash
for data in hashes:
    # data = data[0][1:]
    sentence = 'select timestamp from block where hash=\''+data+'\';\r'
    p.sendline(sentence)
    p.expect('#')
    p.expect('#')

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
query_out = [
    'select timestamp, value from internal_transaction where from_address=\'\\',
    '\' and value!=\'0\';\r'
]
with open('nponzi_out.sql','w') as f:
    for a in addr:
        f.write(query_out[0]+a.strip()+query_out[1])
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

## 机器学习测试结果

使用J48决策树和随机森林算法，十折交叉验证，ponzi 156个，nponzi 135个，正确率大约在80%.下面两张图是目前的测试结果，机器学习的结果是紫色的BehaviorChecker。

![@完美检测场景下评估结果](F:\worktask\信安作品赛\SolPonzi_transaction\metrics-1-1.png)

![@全部测试集下新指标评估结果](F:\worktask\信安作品赛\SolPonzi_transaction\新指标-1-1.png)



可以发现，单独使用SymChecker进行程序分析或者使用BehaviorChecker进行行为分析，难以达到较高的精确度，而使用系统的综合检测方法大大提升了检测器各方面的性能，尤其是将精确度提升到了94%以上。这说明我们的系统检测方法优于普通的单方面检测并且误报率很低，可以极大地降低人工检查的成本，从而达到大规模检测的标准。
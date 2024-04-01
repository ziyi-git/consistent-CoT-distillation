## 2024-04-01
### 目的
在某个数据集上将整个代码运行一遍(以strategyQA为例)。

### 数据
以strategyQA__from_github为例，运行
```python
python ext_build_dataset.py
```
- split_ratio=0.7将train.json分为data_part_1.jsonl（新的train.jsonl）和data_part_2.jsonl（新的dev.jsonl）
- split_ratio=0.7将dev.json转为data_part_1.jsonl（新的test.jsonl）
- 复制并重命名train.jsonl为train.counterfactual.jsonl

获得附带有"explanation"的数据集
```bash
bash spcripts/run_contrastive_decoding.sh
```

微调T5-3b模型
```bash
bash spcripts/run_counterfactual_training.sh
```
log分别保存在debug.log和train_seed_{xx}.log中和test_seed_{xx}.log中。
疑问：在test_seed_{xx}.log中，还出现了choices:[yes, no]？是不是意味着我在制作train.jsonl，dev.jsonl，test.jsonl，train.conuterfactual.jsonl的时候也要加入choices: [yes, no]?




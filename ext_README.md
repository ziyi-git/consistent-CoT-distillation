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
- 复制并重命名train.jsonl为
疑问：train.counterfactual.jsonl中的id还是和train.jsonl的一样？

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

## 2024-04-02
### 目的
在contrastive_decoding_rationalization.py中

**问题1:** train.jsonl将单独用作后续的训练，评估不使用contrastive_decoding的效果？train.counterfactual.jsonl将单独用作后续的训练，评估使用contrastive decoding的效果？dev.jsonl和test.jsonl不用做contrastive decoding，因为它们只参与评估？

**回答1:** 首先从contrastive_decoding_rationalization.py的141至146行看出，train.jsonl，train.counterfactual.jsonl，dev.jsonl和test.jsonl都会做contrastive decoding。

**问题2:** 对train做contrastive decoding的意义是啥？

**回答2:** 公式$G(t_i \mid a^*) = \log {\frac{P(t_i \mid p, q, a^*, t_{< i})}{P(t_i \mid p, q, a^{'}, t_{< i})} }$说明，两种不同情况下（考虑正确答案和错误答案），特定token生成的概率相差越大越好，这会导致G（称为合理性增长plausibility growth）变大。用一个例子来说明：问题->“人类活动是否是全球变暖的主要原因？”，正确答案（$a^{*}$）：“yes”，干扰答案（$a^{'}$）：“no”。当大模型在考虑$a^{*}$后生成rationale时，“碳排放”这个token的概率$P(t_i \mid p, q, a^*, t_{< i})$为0.8，因为“碳排放”和“人类活动”密切相关。在考虑$a^{'}$后生成rationale时，“碳排放”这个token的概率$P(t_i \mid p, q, a^{'}, t_{< i})$只有0.1，因为“人类活动是否是全球变暖的主要原因”时，“碳排放”就关系不大。

**问题3:** 对train.counterfactual也做contrastive decoding的意义是啥？

**回答3:** 对train.counterfactual也做contrastive decoding，是为了让student学习到当答案发生变化后，应当在生成的rationale中强调哪些token。这里的重点是，如果答案错了，模型应该怎样输出explanation来有效地支撑错误的答案。（我既要学会如何输出支撑事实的合理explanation，也要学会输出支撑反事实的合理explanation，只有掌握了本质，才能够指鹿为马）

### 小结
对train做contrastive decoding可以视作为增强，增强那些更具合理性的token生成的概率。对train.counterfactual做contrastive decoding可以视作捕获重点，捕获哪些token生成来应对答案的变化。

**问题4:** prompt的作用是什么？

**回答4:** prompt来自prompts/strategyQA.explanation.txt中的文本（此处以strategyQA为例），将这段文本与训练数据中的每一条QA拼接形成一条prompt来提示teacher模型生成rationales.

例如prompts/strategyQA.explanation.txt："Q: Do hamsters provide food for any animals?\nA: The answer is yes. Hamsters are prey animals. Prey animals provide food for predators.\n\nQ: Could Brooke Shields succeed at University of Pennsylvania?\nA: The answer is yes. Brooke Shields went to Princeton University. Princeton University is about as academically rigorous as the University of Pennsylvania.\n\nQ: Hydrogen's atomic number squared exceeds number of Spice Girls?\nA: The answer is no. Hydrogen has an atomic number of 1. 1 squared is 1. There are 5 Spice Girls.\n\nQ: Is it common to see frost during some college commencements?\nA: The answer is yes. College commencement ceremonies can happen in December, May, and June. December is in the winter, so there can be frost.\n\nQ: Could a llama birth twice during War in Vietnam (1945-46)?\nA: The answer is no. The War in Vietnam was 6 months. The gestation period for a llama is 11 months, which is more than 6 months.\n\nQ: Would a pear sink in water?\nA: The answer is no. The density of a pear is about 0.6 g/cm^3, which is less than water. Objects less dense than water float.\n\nQ: {}\nA: The answer is {}."

训练文本中的一条QA：{"id": "0de2785a6eaba087541a", "question": "Did Jon Brower Minnoch suffer from anorexia nervosa?", "answer": 0}

拼接后的prompt："Q: Do hamsters provide food for any animals?\nA: The answer is yes. Hamsters are prey animals. Prey animals provide food for predators.\n\nQ: Could Brooke Shields succeed at University of Pennsylvania?\nA: The answer is yes. Brooke Shields went to Princeton University. Princeton University is about as academically rigorous as the University of Pennsylvania.\n\nQ: Hydrogen's atomic number squared exceeds number of Spice Girls?\nA: The answer is no. Hydrogen has an atomic number of 1. 1 squared is 1. There are 5 Spice Girls.\n\nQ: Is it common to see frost during some college commencements?\nA: The answer is yes. College commencement ceremonies can happen in December, May, and June. December is in the winter, so there can be frost.\n\nQ: Could a llama birth twice during War in Vietnam (1945-46)?\nA: The answer is no. The War in Vietnam was 6 months. The gestation period for a llama is 11 months, which is more than 6 months.\n\nQ: Would a pear sink in water?\nA: The answer is no. The density of a pear is about 0.6 g/cm^3, which is less than water. Objects less dense than water float.\n\nQ: Did Jon Brower Minnoch suffer from anorexia nervosa?\nA: The answer is no."

**问题5:** indicator_token_ids有什么作用?

**回答5:** indicator_token_ids应该是用一个字典来定义各种特殊token，例如indicator_token_ids['stop']是'\n'。

**问题6:** train和train.counterfactual的example的id相同，对训练是否影响？

**回答6:** 目前看应该对训练没影响，在get_tensor_dataset将数据转为tensor过程中没用到example的"id"信息。

## 2024-04-02
### 目的
在main.py中

**问题1:** get_tensor_dataset对原始数据做了什么处理，处理后的格式是什么样？

**回答1:** 基本上做了两件事：
- 为了不让模型产生混淆，给每一条数据加上[counterfactual]或[factual]前缀。
- 将input和label分开，input是指"question"，label是"explanation" + "answer"。例如input为"[factual] Are the Vietnamese people a great untapped resource for NBA players?"，label则是"[factual] The Vietnamese people are not a great untapped resource for NBA players. So the answer is no"
- 值得注意的是：针对train.counterfactual数据，label有所不同，label同时包括两种：第一个是仅answer，如"yes"。第二个与非counterfactual一样，如"[counterfactual] The NBA needs more Vietnamese players. So the answer is yes"。这个疑问可以在后面回答。

**问题2:** counterfactual_alpha的作用是什么？

**回答2:** counterfactual_alpha若打开（>0）,会将train.counterfactual数据加入训练过程，而这部分数据所产生的loss会以一定权重加入最终的loss。

**问题3:** labels是什么？

**回答3:** 问题1中已经回答，label就是"explanation" + "answer"。

**问题4:** 为什么train包括input_ids, attention_mask, labels，而train.counterfactual则包括input_ids, attention_mask, labels, decoder_input_ids？

**回答4:** 问题1中已经回答，train和train.counterfactual的主要区别是labels vs. labels + decoder_input_ids，实际上train.counterfactual中的decoder_input_ids和train中的labels一样（都是"explanation"+"answer"），train.counterfactual中的label只有"answer"（实际的训练中没有用，可能是作者的代码没真正完成）。

**问题5:** 为什么counterfactual_alpha>0会导致显存显著增大？

**回答5:** counterfactual_alpha>0会再次令模型完成一次前向推理，我的困惑是为什么会导致显存消耗增大这么多，毕竟第二次的前向推理和第一次又不是同时放入显存中。
我的猜测是，在没有运行到loss.backward()之前，所有的推理的显存占用都不会释放。一直到loss.backward()，optimizer.step()，scheduler.step()，optimizer.zero_grad()这些涉及反向传播的步骤完成后，才会释放。

**问题6:** 加载traing，train.counterfactual和dev使用的是get_tensor_dataset，但加载test用的是load_raw_dataset？

**回答6:** 其实load_raw_dataset和ext_build_dataset.py的作用是一样的，都是把数据组织成{'id': '***', 'explanation': '***', 'answer': '***'}的形式。


**问题7:** 测试test时用了三个推理接口，inference，inference_with_oracle，inference_with_perturb，区别是什么？这三个接口都返回了accuracy，accuracy怎么算的？为什在评估dev数据集时，又用的是evaluate？

**回答7:** 
inference，inference_with_oracle，inference_with_perturb使用了三种不同的方式计算answer（yes或no）的预测准确率，这里我并没有进行深究。evaluate：主要计算perplexity：$PPL=e^{(\frac{1}{N}\sum_{i=1}^{N}Loss_{i})}$。其中N是总的token数，${Loss_i}$是第i个token的损失。这里的损失一般都是交叉熵损失。


## 2024-04-11
从开始看这篇论文到现在，花费了3周的时间。本身的预期是想以strategyQA为对象，复现论文中的结果。但是这个论文的代码并不完整，当然也确实给出了比较核心的代码，比如构建contractive decoding，构建从counterfactual数据。如果完整的去实现论文中的结果部分，还需要牵扯到其它的论文。考虑时间上的有限，而且对于学习这篇论文的目的仅限于搞懂CoT，以及如何训练模型，所以暂时到此为止。

### 小结

对teacher model的生成explanation的过程施加contrastive decoding，生成与answer更相关的explanation。

利用teacher model生成的数据对student model进行训练，验证和测试。
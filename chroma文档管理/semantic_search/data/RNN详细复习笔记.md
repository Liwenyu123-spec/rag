# RNN 详细复习笔记

> 电脑里原先没有对应复习文件，本篇从零写成（序列入门向）。  
> 姊妹篇：神经网络与 MLP、CNN、Transformer、PyTorch 训练实战。  
> 公式：`$...$` / `$$...$$`。

---

## 〇、一句话抓住全篇

> **RNN 用同一个网络单元沿时间步扫序列，隐状态记住「读到现在」的摘要，适合文本、时间序列等有顺序的数据。**

| 章 | 内容 |
| --- | --- |
| 一 | 序列问题与为何要循环 |
| 二 | 基础 RNN 公式 |
| 三 | BPTT、梯度消失与 LSTM/GRU |
| 四 | 任务头：分类 / 生成 / seq2seq 直觉 |
| 五 | PyTorch 代码 |
| 六 | 易错点与自测 |

---

## 一、序列数据要什么

样本不是固定长度特征向量，而是一串：

$$
x_1,x_2,\ldots,x_T
$$

例如：词序列、每日销量、传感器读数。

| 做法 | 问题 |
| --- | --- |
| 截断/填充后喂 MLP | 难显式利用顺序与变长 |
| CNN 一维卷积 | 能抓局部模式，长依赖要很深/大核 |
| RNN | 逐步更新记忆，天生吃顺序 |

---

## 二、基础 RNN

每步共享参数，更新隐状态 $h_t$：

$$
h_t=\tanh(W_{xh}x_t+W_{hh}h_{t-1}+b_h)
$$

输出（若需要每步一个）：

$$
y_t=W_{hy}h_t+b_y
$$

| 符号 | 含义 |
| --- | --- |
| $x_t$ | 第 $t$ 步输入 |
| $h_t$ | 隐状态（短期记忆） |
| 共享 $W$ | 所有时间步同一套权重 |

人话：读下一个词时，既看当前词，也看「之前读完后脑子里剩的印象」。

形状直觉（batch 优先常见写法）：

- 输入：`(batch, seq, input_size)` 或 `(seq, batch, input_size)`  
- 输出隐状态：`(batch, seq, hidden_size)`  
- 最后一层最终 $h_T$：常拿去做整句分类  

---

## 三、训练难点与 LSTM / GRU

### 3.1 BPTT

沿展开的时间链反传，叫 **BPTT（Backprop Through Time）**。  
序列很长 → 图很深 → 梯度易 **消失**（或爆炸）。

缓解：梯度裁剪、门控结构、短序列/截断 BPTT。

### 3.2 LSTM（长短期记忆）

用 **输入门 / 遗忘门 / 输出门** 和细胞状态 $c_t$，更擅长保留长距离信息。  
不必考试默写全部公式，记住：

> 门控决定「记什么、忘什么、读出什么」。

### 3.3 GRU

LSTM 的简化版，参数更少，很多任务效果接近，训练更快。

| | 朴素 RNN | GRU | LSTM |
| --- | --- | --- | --- |
| 长依赖 | 弱 | 较强 | 较强 |
| 参数量 | 少 | 中 | 更多 |
| 入门选用 | 理解原理 | **常用默认** | 也很常用 |

现代 NLP 大任务多被 Transformer 取代，但时间序列、小模型、流式场景 RNN/LSTM 仍常见。

---

## 四、常见任务形态

| 任务 | 用法直觉 |
| --- | --- |
| 序列分类 | 编码整段 → 用最后 $h_T$（或池化）→ Linear |
| 词性/逐帧标注 | 每步一个输出头 |
| 语言模型 | 预测下一个 token |
| Seq2Seq | 编码器 RNN 压成向量，解码器 RNN 生成（注意力出现后演进到 Transformer） |

双向 RNN：正反向各扫一遍再拼接，适合「能看全文」的标注/分类（不能用于严格因果生成）。

---

## 五、综合代码（情感分类风小例子）

```python
import torch  # PyTorch
import torch.nn as nn  # 模块
from torch.utils.data import DataLoader, TensorDataset  # 数据

torch.manual_seed(42)  # 种子
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 设备

# ---------- 假数据：batch 条序列，长度 T，词表嵌入后已是向量 ----------
B, T, V, H, C = 32, 20, 100, 64, 2  # batch/长度/词表/隐/类数
# 实际应 Embedding(token_id)；这里直接随机浮点充当「已嵌入」
X = torch.randn(B, T, 32)  # (batch, seq, input_size)
y = torch.randint(0, C, (B,))  # 类别
loader = DataLoader(TensorDataset(X, y), batch_size=8, shuffle=True)  # loader

class RNNClassifier(nn.Module):  # 序列分类
    def __init__(self, input_size, hidden_size, num_classes):  # 尺寸
        super().__init__()  # 父类
        self.rnn = nn.GRU(  # 用 GRU 更稳
            input_size=input_size,  # 输入维
            hidden_size=hidden_size,  # 隐维
            num_layers=1,  # 层数
            batch_first=True,  # (B,T,F)
            bidirectional=False,  # 单向；需要可改 True
        )
        self.fc = nn.Linear(hidden_size, num_classes)  # 分类头（双向则 hidden*2）

    def forward(self, x):  # x: (B,T,F)
        out, h_n = self.rnn(x)  # out:(B,T,H)  h_n:(1,B,H)
        last = h_n[-1]  # 取最后一层最终隐状态 (B,H)
        return self.fc(last)  # logit (B,C)

model = RNNClassifier(32, H, C).to(device)  # 模型
opt = torch.optim.Adam(model.parameters(), lr=1e-3)  # 优化器
crit = nn.CrossEntropyLoss()  # 损失

model.train()  # 训练
xb, yb = next(iter(loader))  # 一个 batch
xb, yb = xb.to(device), yb.to(device)  # 上设备
logit = model(xb)  # 前向
loss = crit(logit, yb)  # 损失
opt.zero_grad()  # 清梯度
loss.backward()  # 反传（内部已是 BPTT）
nn.utils.clip_grad_norm_(model.parameters(), 1.0)  # 梯度裁剪防爆
opt.step()  # 更新
print("logit", tuple(logit.shape), "loss", float(loss))  # 验形
```

有真实 token 时：先 `nn.Embedding`，再 RNN；变长序列用 `pack_padded_sequence`（进阶，知道有这回事即可）。

---

## 六、易错点与自测

1. `batch_first` 和输入形状不一致。  
2. 分类误用「所有时间步输出的平均」或「错层的 h_n」却不自知——先打印 shape。  
3. 长序列不裁剪梯度，LSTM 也可能炸。  
4. 生成任务用了双向 RNN（泄漏未来）。  
5. 能上 Transformer 的大数据 NLP 仍死磕深层朴素 RNN。  

自测：RNN 相对 MLP 多了什么？BPTT 是什么？LSTM/GRU 为解决什么？分类常用哪个向量？  
答案：沿时间共享的隐状态；沿时间反传；长依赖/梯度消失；常最后隐状态（或池化）。

---

## 七、一句话收束

> RNN 族用循环隐状态吃顺序；入门用 GRU/LSTM + 最后状态分类，长文本与大规模 NLP 再转向 Transformer。

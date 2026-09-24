# Transformer 详细复习笔记

> 电脑里原先没有对应复习文件，本篇从零写成（原理 + 最小直觉代码）。  
> 姊妹篇：RNN、CNN、神经网络与 MLP、PyTorch 训练实战。  
> 公式：`$...$` / `$$...$$`。

---

## 〇、一句话抓住全篇

> **Transformer 不靠循环扫时间，而用自注意力让序列中任意位置直接交互；叠加前馈、残差与层归一化，成为现代 NLP / 多模态的骨干。**

| 章 | 内容 |
| --- | --- |
| 一 | 从 RNN 到注意力 |
| 二 | Scaled Dot-Product Attention |
| 三 | 多头、残差、FFN、位置编码 |
| 四 | Encoder / Decoder / 因果掩码 |
| 五 | 与 RNN 对比与选型 |
| 六 | 代码直觉 |
| 七 | 易错点与自测 |

---

## 一、痛点与思路

RNN：逐步传隐状态 → 长距离要跨很多步，难并行。  

**注意力**：算「当前词该看哪些词、看多少」，一步内建立全局（或窗口内）联系，矩阵运算易并行。

自注意力（Self-Attention）：Query / Key / Value 都来自同一序列。

---

## 二、Scaled Dot-Product Attention

对输入投影得到 $Q,K,V$：

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

| 符号 | 人话 |
| --- | --- |
| $Q$ | 我在找什么 |
| $K$ | 我有什么标签可被对上 |
| $V$ | 对上之后取出的内容 |
| $QK^\top$ | 相似度分数 |
| $\sqrt{d_k}$ | 缩放，防点积过大导致 softmax 极尖、梯度变差 |
| softmax | 变成权重 |
| ×$V$ | 加权汇总 |

输出与序列长度相关的注意力权重，决定信息混合方式。

---

## 三、多头、子层与位置编码

### 3.1 Multi-Head Attention

多套 $QKV$ 投影并行，各自盯不同关系（句法、指代等直觉），再拼起来投影回去。

### 3.2 每个 Encoder 块大致

```text
x → Multi-Head Attn → Dropout → +x（残差）→ LayerNorm
  → FFN(两层线性+激活) → Dropout → + → LayerNorm
```

（Pre-LN / Post-LN 变体顺序略有不同，知道「残差 + 归一化 + FFN」即可。）

### 3.3 位置编码 Positional Encoding

注意力本身 **置换不敏感**（打乱顺序分数结构会变但模型无内置「位置」）。  
故要加位置信息：正弦位置编码或可学习 `nn.Embedding` 位置向量。

---

## 四、Encoder、Decoder、掩码

| 结构 | 典型用途 |
| --- | --- |
| Encoder only（BERT 风） | 理解、分类、填空（双向） |
| Decoder only（GPT 风） | 自回归生成 |
| Encoder-Decoder（原版机器翻译） | 序列到序列 |

**因果掩码（causal mask）**：生成时位置 $t$ 不能看 $t$ 之后，否则「偷看未来」。  
Padding mask：忽略 pad 位置，别让注意力打到填充符上。

---

## 五、和 RNN 怎么选

| | RNN/LSTM | Transformer |
| --- | --- | --- |
| 并行 | 时间步难并行 | 序列内高度并行 |
| 长依赖 | 门控缓解，仍吃力 | 直接连边，更擅长（长度受内存限制） |
| 数据/算力 | 小数据小模型更轻 | 大数据大体量更强 |
| 归纳偏置 | 强顺序偏置 | 更靠数据与位置编码 |

小作业情感分类：GRU 往往够。  
大语料预训练 / 翻译 / 大模型：Transformer。

---

## 六、综合代码（官方层走通 + 手写注意力形状）

```python
import math  # 平方根
import torch  # PyTorch
import torch.nn as nn  # 模块
import torch.nn.functional as F  # 函数式

torch.manual_seed(0)  # 种子
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 设备

# ---------- 1) 手写单头注意力，盯形状 ----------
B, T, D = 2, 5, 8  # batch、长度、维度
dk = D  # 简化：头维=模型维
x = torch.randn(B, T, D, device=device)  # 输入
Wq = nn.Linear(D, dk).to(device)  # Q 投影
Wk = nn.Linear(D, dk).to(device)  # K
Wv = nn.Linear(D, dk).to(device)  # V
Q, K, V = Wq(x), Wk(x), Wv(x)  # (B,T,dk)
scores = (Q @ K.transpose(-2, -1)) / math.sqrt(dk)  # (B,T,T) 每位置对所有位置打分
weights = torch.softmax(scores, dim=-1)  # 注意力权重
out = weights @ V  # (B,T,dk) 加权值
print("attn out", tuple(out.shape), "weights", tuple(weights.shape))  # 验形

# ---------- 2) 因果掩码：下三角可见 ----------
mask = torch.tril(torch.ones(T, T, device=device))  # 下三角 1
scores_masked = scores.masked_fill(mask == 0, float("-inf"))  # 未来置 -inf
weights_causal = torch.softmax(scores_masked, dim=-1)  # 未来权重变 0
print("causal row0", weights_causal[0, 0].detach().cpu().numpy().round(3))  # 第 0 步只看自己

# ---------- 3) 用 nn.TransformerEncoder 做序列分类骨架 ----------
class TinyTransformerClassifier(nn.Module):  # 分类器
    def __init__(self, vocab_size, d_model, nhead, num_classes, nlayers=2, max_len=128):  # 超参
        super().__init__()  # 父类
        self.embed = nn.Embedding(vocab_size, d_model)  # token 嵌入
        self.pos = nn.Embedding(max_len, d_model)  # 可学习位置
        layer = nn.TransformerEncoderLayer(  # 单层定义
            d_model=d_model, nhead=nhead, dim_feedforward=4 * d_model,  # FFN 变宽
            batch_first=True,  # (B,T,D)
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=nlayers)  # 堆叠
        self.fc = nn.Linear(d_model, num_classes)  # 分类头

    def forward(self, token_ids):  # (B,T)
        B, T = token_ids.shape  # 尺寸
        positions = torch.arange(T, device=token_ids.device).unsqueeze(0).expand(B, T)  # 位置索引
        x = self.embed(token_ids) + self.pos(positions)  # 嵌入+位置
        x = self.encoder(x)  # (B,T,D)
        pooled = x.mean(dim=1)  # 平均池化；也可用 [CLS] 位
        return self.fc(pooled)  # logit

model = TinyTransformerClassifier(vocab_size=1000, d_model=64, nhead=4, num_classes=3).to(device)  # 建模型
ids = torch.randint(0, 1000, (8, 20), device=device)  # 假 token
logits = model(ids)  # 前向
loss = F.cross_entropy(logits, torch.randint(0, 3, (8,), device=device))  # 损失
loss.backward()  # 反传一步，确保可训
print("logits", tuple(logits.shape), "loss", float(loss))  # 打印
```

真实训练仍要：padding mask、学习率 warmup、更大数据与正则；大模型直接调 `transformers` 库预训练权重更常见。

---

## 七、易错点与自测

1. 忘记除以 $\sqrt{d_k}$。  
2. 生成不用因果掩码，训练指标虚高。  
3. `batch_first` 与 `nn.Transformer*` 默认历史 API 不一致——查清参数。  
4. 忽略位置编码，顺序任务变差。  
5. 序列很长时 $T\times T$ 注意力显存爆炸（需长序列变体/稀疏注意力，了解即可）。  

自测：Attention 公式？为何要 scale？多头图什么？GPT 类为何要因果掩码？相对 RNN 最大工程优势？  
答案：$softmax(QK^\top/\sqrt{d_k})V$；防点积过大；多组关系子空间；禁止看未来；训练并行。

---

## 八、一句话收束

> Transformer 用缩放点积注意力做全局交互，再叠多头、残差、FFN 与位置信息；弄清 $QKV$、掩码与 Encoder/Decoder 分工，就能读懂 BERT/GPT 类模型的骨架。

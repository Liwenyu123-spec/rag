# Softmax与多分类详细复习笔记

> 对照语雀《2 深度学习》§2.5「多分类问题」。  
> 姊妹篇：逻辑回归、神经网络与 MLP、PyTorch 训练实战、CNN。  
> 公式：`$...$` / `$$...$$`。

---

## 〇、一句话抓住全篇

> **多分类：模型先输出各类别的分数（logit），用 Softmax 变成概率，再取最大类；训练常用交叉熵（PyTorch 的 `CrossEntropyLoss` 已内置 Softmax）。**

| 章 | 内容 |
| --- | --- |
| 一 | 从二分类到多分类 |
| 二 | Softmax |
| 三 | 交叉熵与 `CrossEntropyLoss` |
| 四 | 代码 |
| 五 | 易错点与自测 |

---

## 一、二分类 vs 多分类

| | 二分类 | 多分类（$K$ 类） |
| --- | --- | --- |
| 输出 | 1 个分数 / 概率 | $K$ 个分数 |
| 概率变换 | Sigmoid | Softmax |
| 常用损失 | `BCEWithLogitsLoss` | `CrossEntropyLoss` |
| 决策 | 阈值（常 0.5） | $\arg\max$ 概率或 logit |

逻辑回归套 Sigmoid = 二分类；输出层 $K$ 维 + Softmax = 多类逻辑回归 / Softmax 回归。

---

## 二、Softmax

对一类分数向量 $z=(z_1,\ldots,z_K)$：

$$
p_k=\frac{e^{z_k}}{\sum_{j=1}^{K}e^{z_j}}
$$

性质：

- $p_k\in(0,1)$，且 $\sum_k p_k=1$  
- $z_k$ 越大，$p_k$ 越大  
- 预测类别：$\hat{y}=\arg\max_k p_k$（与直接对 logit 取 argmax 结果相同）

人话：把「各类打分」拧成「各类概率，加起来等于 1」。

---

## 三、交叉熵损失

真实类别为 $y$（独热或类别下标），预测概率 $p$：

$$
L=-\sum_{k=1}^{K} y_k\log p_k
$$

只保留真实类那一项时：$L=-\log p_{y}$。  
预测对且概率高 → 损失小；错得很笃定 → 损失大。

**PyTorch 注意：**

```python
nn.CrossEntropyLoss()  # 输入是 logit，标签是 Long 类别下标
# 不要先 Softmax 再喂给它（内部已含 log-softmax）
```

与 `NLLLoss`：若你手动 `log_softmax`，再用 NLL；入门直接用 `CrossEntropyLoss` 即可。

---

## 四、综合代码（逐行注释）

```python
import torch  # PyTorch
import torch.nn as nn  # 模块
import torch.nn.functional as F  # Softmax 等

torch.manual_seed(0)  # 种子

# ---------- Softmax 直觉 ----------
logits = torch.tensor([2.0, 1.0, 0.1])  # 三类分数
probs = torch.softmax(logits, dim=0)  # 概率
print("probs:", probs.tolist(), "sum=", float(probs.sum()))  # 和为 1
print("pred class:", int(torch.argmax(probs)))  # 取最大

# ---------- 小网络多分类 ----------
X = torch.randn(64, 10)  # 64 个样本，10 维特征
y = torch.randint(0, 3, (64,))  # 3 类标签 0/1/2

model = nn.Sequential(  # 简单 MLP
    nn.Linear(10, 16),  # 隐层
    nn.ReLU(),  # 激活
    nn.Linear(16, 3),  # 3 个 logit
)
crit = nn.CrossEntropyLoss()  # 交叉熵（吃 logit）
opt = torch.optim.Adam(model.parameters(), lr=1e-2)  # 优化器

for step in range(50):  # 训练几步
    logit = model(X)  # (64,3)
    loss = crit(logit, y)  # 与 Long 标签
    opt.zero_grad()  # 清梯度
    loss.backward()  # 反传
    opt.step()  # 更新

with torch.no_grad():  # 评估
    pred = model(X).argmax(dim=1)  # 预测类
print("acc:", float((pred == y).float().mean()))  # 训练准确率（示意）

# 错误示范（不要这样做）：
# p = F.softmax(logit, dim=1)
# loss = crit(p, y)  # 相当于 Softmax 了两次，数值与语义都错
```

---

## 五、易错点与自测

1. `CrossEntropyLoss` 前又手写 Softmax。  
2. 标签做成 one-hot float 却接默认 CE（应用类别索引 Long；或改用其他损失形式）。  
3. 二分类硬上 Softmax 两维，却用不好的标签编码。  
4. 把 Softmax 概率再取阈值当二分类那套（多分类直接 argmax）。  

自测：Softmax 输出有何约束？多分类默认损失？CE 吃 logit 还是概率？  
答案：非负且和为 1；交叉熵；logit（在 PyTorch CE 中）。

---

## 六、一句话收束

> 多分类三步：打分 → Softmax 成概率 → 交叉熵监督；记住 PyTorch 里 CE 与 Softmax 不要叠两层。

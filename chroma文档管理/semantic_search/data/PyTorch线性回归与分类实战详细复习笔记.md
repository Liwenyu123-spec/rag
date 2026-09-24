# PyTorch线性回归与分类实战详细复习笔记

> 对照语雀《2 深度学习》§2.3 线性回归、§2.4 二分类、§2.5 多分类。  
> 姊妹篇：Softmax与多分类、反向传播与优化器、PyTorch 训练实战、线性/逻辑回归。  
> 公式：`$...$` / `$$...$$`。

---

## 〇、一句话抓住全篇

> **用 PyTorch 重做三件监督学习小事：线性回归（MSE）、二分类（BCE+Logits）、多分类（CrossEntropy）；体会张量、自动求导与训练三连。**

| 章 | 内容 |
| --- | --- |
| 一 | 与 sklearn 对照 |
| 二 | 线性回归 |
| 三 | 二分类 |
| 四 | 多分类 |
| 五 | 易错点与自测 |

---

## 一、和经典 ML 的关系

| 任务 | 经典课 | PyTorch 写法 |
| --- | --- | --- |
| 回归 | `LinearRegression` | `nn.Linear` + `MSELoss` |
| 二分类 | `LogisticRegression` | `nn.Linear` + `BCEWithLogitsLoss` |
| 多分类 | Softmax 回归 / MLP | `nn.Linear(..., K)` + `CrossEntropyLoss` |

深度课重点是：**手写训练循环**，不是换个更强模型。

---

## 二、线性回归（逐行注释）

```python
import torch  # PyTorch
import torch.nn as nn  # 模块

torch.manual_seed(0)  # 种子
# 真关系 y = 3x + 2 + 噪声
X = torch.linspace(-1, 1, 100).unsqueeze(1)  # (100,1)
y = 3 * X + 2 + 0.1 * torch.randn_like(X)  # 标签

model = nn.Linear(1, 1)  # y = wx+b
crit = nn.MSELoss()  # 均方误差
opt = torch.optim.SGD(model.parameters(), lr=0.1)  # SGD

for epoch in range(200):  # 训练
    pred = model(X)  # 前向
    loss = crit(pred, y)  # 损失
    opt.zero_grad()  # 清梯度
    loss.backward()  # 反传
    opt.step()  # 更新

w = float(model.weight.data)  # 学到的斜率
b = float(model.bias.data)  # 截距
print("w,b ≈", round(w, 3), round(b, 3), "loss", float(loss))  # 应接近 3,2
```

---

## 三、二分类（逐行注释）

语雀口径：线性打分 → Sigmoid 成概率 → 阈值分类。  
工程上更推荐 **BCEWithLogitsLoss**（数值稳）。

```python
import torch  # PyTorch
import torch.nn as nn  # 模块

torch.manual_seed(0)  # 种子
N = 200  # 样本
X = torch.randn(N, 2)  # 两维特征
y = ((X[:, 0] + 0.8 * X[:, 1]) > 0).float().unsqueeze(1)  # 线性可分标签

model = nn.Linear(2, 1)  # 一个 logit
crit = nn.BCEWithLogitsLoss()  # 内含 Sigmoid
opt = torch.optim.Adam(model.parameters(), lr=0.05)  # Adam

for epoch in range(300):  # 训练
    logit = model(X)  # 打分
    loss = crit(logit, y)  # 损失
    opt.zero_grad()  # 清梯度
    loss.backward()  # 反传
    opt.step()  # 更新

with torch.no_grad():  # 评估
    prob = torch.sigmoid(model(X))  # 概率
    pred = (prob >= 0.5).float()  # 阈值 0.5
print("acc", float((pred == y).float().mean()))  # 准确率
```

---

## 四、多分类（逐行注释）

详见姊妹篇《Softmax与多分类》；此处对齐语雀最小闭环。

```python
import torch  # PyTorch
import torch.nn as nn  # 模块

torch.manual_seed(0)  # 种子
N, D, K = 300, 4, 3  # 样本、特征、类数
X = torch.randn(N, D)  # 特征
y = torch.randint(0, K, (N,))  # 类别下标

model = nn.Sequential(  # 可加隐藏层
    nn.Linear(D, 16), nn.ReLU(),  # 隐层
    nn.Linear(16, K),  # K 个 logit
)
crit = nn.CrossEntropyLoss()  # Softmax+CE 内置
opt = torch.optim.Adam(model.parameters(), lr=1e-2)  # 优化器

for epoch in range(200):  # 训练
    loss = crit(model(X), y)  # 前向+损失
    opt.zero_grad()  # 清梯度
    loss.backward()  # 反传
    opt.step()  # 更新

with torch.no_grad():  # 评估
    pred = model(X).argmax(1)  # argmax
print("acc", float((pred == y).float().mean()))  # 准确率
```

---

## 五、易错点与自测

1. 回归用 CE、分类用 MSE（任务-损失配错）。  
2. 二分类用 CE 却只输出 1 维且标签是 `{0,1}` 时，更该用 BCE With Logits。  
3. 多分类 CE 前再 Softmax。  
4. 忘记 `zero_grad`。  

自测：三任务默认损失？二分类概率怎么来？多分类预测怎么取？  
答案：MSE / BCEWithLogits / CrossEntropy；sigmoid(logit)；argmax(logit)。

---

## 六、一句话收束

> 语雀深度学习入门的编程主线，就是用自动求导把线性回归、二分类、多分类各跑通一遍；这三块通了，再叠 CNN 只是换骨干。

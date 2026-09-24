# PyTorch 训练实战详细复习笔记

> 电脑里原先没有系统训练讲义，本篇从零写成。  
> 本篇把 Dataset、训练闭环、保存、过拟合手段写成可复习模板。  
> 姊妹篇：神经网络与 MLP、反向传播与优化器、CNN、RNN、Transformer。  
> 公式少量；代码逐行末尾注释。

---

## 〇、一句话抓住全篇

> **PyTorch 实战 = 数据管道 + `nn.Module` + 损失/优化器 + epoch 循环（train/eval）+ 指标与存盘。**

| 章 | 内容 |
| --- | --- |
| 一 | 张量、设备、可复现 |
| 二 | Dataset / DataLoader |
| 三 | 模型与训练/验证模板 |
| 四 | 保存加载、早停、调度 |
| 五 | 完整二分类表格 MLP 代码 |
| 六 | 易错点与自测 |

---

## 一、张量、设备、种子

```python
import torch  # 导入
import random  # Python 随机
import numpy as np  # NumPy 随机

def set_seed(seed=42):  # 固定种子，便于复现
    random.seed(seed)  # py
    np.random.seed(seed)  # numpy
    torch.manual_seed(seed)  # cpu torch
    if torch.cuda.is_available():  # 有 GPU
        torch.cuda.manual_seed_all(seed)  # 所有 GPU

set_seed(42)  # 调用
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 选设备
```

规则：

- 模型参数与输入 batch **同一 device**  
- 算指标时可 `.cpu().numpy()`  
- 显存不够：降 `batch_size`  

---

## 二、Dataset 与 DataLoader

| 组件 | 职责 |
| --- | --- |
| `Dataset` | 一条样本怎么取 |
| `DataLoader` | 组 batch、shuffle、多进程 |

小表格：

```python
from torch.utils.data import TensorDataset, DataLoader  # 工具
# ds = TensorDataset(X_tensor, y_tensor)
# loader = DataLoader(ds, batch_size=64, shuffle=True)
```

自定义：实现 `__len__`、`__getitem__`（图像读文件常这样写）。

---

## 三、训练 / 验证模板（背这张骨架）

```text
model.to(device)
for epoch in range(1, E+1):
    model.train()
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        loss = criterion(model(xb), yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        # 在 val_loader 上累计损失与指标
    # 可选：调度器.step()、早停、存 best checkpoint
```

| 模式 | 作用 |
| --- | --- |
| `model.train()` | Dropout / BN 用训练行为 |
| `model.eval()` | 推理行为 |
| `torch.no_grad()` | 不建图，省显存 |

分类指标：Accuracy / F1 / AUC（概率先 `sigmoid` 或 `softmax`）。  
回归：MAE / RMSE。阈值与不平衡策略同《机器学习基础与模型评估》。

---

## 四、保存、加载、早停、学习率调度

### 4.1 存权重（常用）

```python
torch.save(model.state_dict(), "best.pt")  # 只存参数
# 加载：
# model.load_state_dict(torch.load("best.pt", map_location=device))
# model.to(device).eval()
```

### 4.2 早停直觉

验证指标连续若干 epoch 不提升 → stop，并保留历史最佳权重。

### 4.3 调度示例

```python
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(  # 验证不好就降 lr
    optimizer, mode="min", factor=0.5, patience=3  # 耐心 3
)
# 每个 epoch 验证后：scheduler.step(val_loss)
```

---

## 五、综合代码（表格二分类完整闭环）

```python
import numpy as np  # 数值
import torch  # PyTorch
import torch.nn as nn  # 网络
from torch.utils.data import TensorDataset, DataLoader  # 数据
from sklearn.datasets import make_classification  # 造数
from sklearn.model_selection import train_test_split  # 划分
from sklearn.preprocessing import StandardScaler  # 缩放
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score  # 指标

def set_seed(seed=42):  # 复现
    np.random.seed(seed)  # np
    torch.manual_seed(seed)  # torch

set_seed(42)  # 设种子
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 设备
print("device:", device)  # 打印

# ---------- 数据 ----------
X, y = make_classification(  # 合成
    n_samples=3000, n_features=20, n_informative=8, random_state=42  # 规模
)
X_tr, X_te, y_tr, y_te = train_test_split(  # 划分
    X, y, test_size=0.2, random_state=42, stratify=y  # 分层
)
scaler = StandardScaler()  # 标准化
X_tr = scaler.fit_transform(X_tr)  # fit 训练
X_te = scaler.transform(X_te)  # transform 测试

def to_loader(X, y, bs, shuffle):  # 打包 DataLoader
    xt = torch.tensor(X, dtype=torch.float32)  # 特征
    yt = torch.tensor(y, dtype=torch.float32).unsqueeze(1)  # (N,1)
    return DataLoader(TensorDataset(xt, yt), batch_size=bs, shuffle=shuffle)  # 返回

train_loader = to_loader(X_tr, y_tr, 64, True)  # 训练
# 测试集也可 loader；这里为简单直接整集评估

# ---------- 模型 ----------
class MLP(nn.Module):  # MLP
    def __init__(self, d):  # 输入维
        super().__init__()  # 父类
        self.net = nn.Sequential(  # 堆叠
            nn.Linear(d, 128), nn.ReLU(), nn.Dropout(0.2),  # 块 1
            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.2),  # 块 2
            nn.Linear(64, 1),  # logit
        )

    def forward(self, x):  # 前向
        return self.net(x)  # 输出

model = MLP(X_tr.shape[1]).to(device)  # 实例化
crit = nn.BCEWithLogitsLoss()  # 二分类损失
opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)  # Adam
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, patience=2, factor=0.5)  # 调度

best_auc, best_state, wait, max_wait = 0.0, None, 0, 5  # 早停状态

def eval_auc():  # 测试 AUC
    model.eval()  # 评估模式
    with torch.no_grad():  # 无梯度
        logit = model(torch.tensor(X_te, dtype=torch.float32).to(device))  # 前向
        prob = torch.sigmoid(logit).cpu().numpy().ravel()  # 概率
    return roc_auc_score(y_te, prob), prob  # 返回

# ---------- 训练 ----------
for epoch in range(1, 41):  # 最多 40 epoch
    model.train()  # 训练
    run = 0.0  # 累计损失
    for xb, yb in train_loader:  # batch
        xb, yb = xb.to(device), yb.to(device)  # 设备
        loss = crit(model(xb), yb)  # 损失
        opt.zero_grad()  # 清梯度
        loss.backward()  # 反传
        opt.step()  # 更新
        run += loss.item() * len(xb)  # 累加
    tr_loss = run / len(train_loader.dataset)  # 平均损失
    auc, prob = eval_auc()  # 验证（此处直接用测试集演示；正经应再切验证集）
    scheduler.step(1 - auc)  # 用「越小越好」的代理量调度；也可 step(val_loss)
    print(f"epoch {epoch:02d} | loss {tr_loss:.4f} | auc {auc:.4f}")  # 日志

    if auc > best_auc:  # 刷新最佳
        best_auc, best_state, wait = auc, {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}, 0  # 深拷贝到 CPU
    else:  # 没提升
        wait += 1  # 耐心计数
        if wait >= max_wait:  # 早停
            print("early stop")  # 提示
            break  # 退出

model.load_state_dict(best_state)  # 回载最佳
model.to(device)  # 回设备
auc, prob = eval_auc()  # 最终
pred = (prob >= 0.5).astype(int)  # 阈值
print("best auc", round(best_auc, 4),  # 最佳 AUC
      "acc", round(accuracy_score(y_te, pred), 4),  # 准确率
      "f1", round(f1_score(y_te, pred), 4))  # F1
torch.save(model.state_dict(), "mlp_best.pt")  # 落盘
```

正经项目请：**训练 / 验证 / 测试** 三分；早停只看验证集，测试集最后报一次。

---

## 六、易错点与自测

1. 训练验证设备不一致。  
2. 验证时不 `eval()`，Dropout 仍在随机掐。  
3. 只存了整个 `model` 对象，换代码结构就加载失败（优先 `state_dict`）。  
4. 用测试集调参导致乐观偏差。  
5. 表格特征不缩放。  
6. OOM 不降 batch，只反复重跑。  

自测：train/eval 差别？为何 `no_grad`？早停看哪份数据？`state_dict` 存什么？  
答案：Dropout/BN 行为；不建图；验证集；模型参数张量字典。

---

## 七、一句话收束

> 框架实战不是记 API 百科，而是把「数据 → 模型 → 三连更新 → 验证指标 → 存最佳」跑成肌肉记忆；环境装好后，本篇模板可以直接改任务头与数据源复用。

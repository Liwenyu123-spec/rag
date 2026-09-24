# SVM 详细复习笔记

> 材料：`SVM_Kmeans_PCA导引课.html`、`SVM_Kmeans_PCA_总览.pdf`、`SVM_Kmeans_PCA_课件.md`，以及《昨今两日讲义详细汇总》。  
> 写法对齐《集成学习详细笔记》：直觉 → 公式 → 工程要点 → 逐行注释代码 → 易错点 → 自测。  
> 公式：Typora 0.94 用 `$...$` / `$$...$$`。  
> 姊妹篇：`K-Means详细复习笔记.md`、`PCA详细复习笔记.md`。

---

## 〇、这份笔记怎么用

总览一句话：

> **SVM 解决有监督分类：寻找最稳健的最大间隔边界。**  
> 不只是「分开两类」，而是离两边最近的点尽可能远，让泛化更稳。

选型定位（总览「算法选型第一法则」）：

| 维度 | SVM |
| --- | --- |
| 标签 | **有标签**（监督） |
| 业务痛点 | 预测复杂的类别边界 |
| 视觉隐喻 | 带安全边界的切割线 / 「公路」 |
| 核心输出 | 类别判定（可再要概率） |

| 章 | 内容 |
| --- | --- |
| 一 | 几何直觉、术语、与树/集成对比 |
| 二 | 硬间隔 / 软间隔与公式 |
| 三 | `C`、核函数、`gamma` |
| 四 | 标准化、Pipeline、不平衡 |
| 五 | 案例与综合代码 |
| 六 | 易错点、自测、练习 |

```python
# pip install scikit-learn pandas numpy matplotlib
```

---

## 一、几何直觉与术语

### 1.1 核心直觉（总览原话）

分类器本质：给样本画一条分界。只「分开」不够——边界贴着样本，稍有噪声就翻车。

SVM 的灵魂是 **最大间隔（maximum margin）**：

- 中间那条实线 = **决策边界**
- 两侧虚线夹出的带宽 = **间隔（margin）**，像一条公路
- 贴在路边、撑住公路宽度的关键样本 = **支持向量（support vectors）**

> 挪走非支持向量，边界往往不变；支持向量才真正决定模型。

典型案例：互联网平台客户流失 —— 流失用户 vs 续费用户，找最宽安全缝。

### 1.2 术语卡

| 术语 | 人话 |
| --- | --- |
| 样本 / 特征 / 标签 | 一个对象、它的属性、它的类别 |
| 决策边界 | 分开两类的线 / 面 / 超平面 |
| 间隔 | 边界到最近样本的距离 |
| 支持向量 | 贴在间隔边缘的样本 |
| 硬间隔 | 必须完美分开，现实中常过严 |
| 软间隔 | 允许少量越界，用 $C$ 惩罚 |
| 核函数 | 隐式升维，处理非线性 |
| `Pipeline` | 标准化 + 模型绑在一起上线 |

### 1.3 和已学模型对比

| | 决策树 | 集成（森林等） | SVM |
| --- | --- | --- | --- |
| 思路 | if-else 切空间 | 多模型投票/纠错 | 几何上找最宽缝 |
| 尺度 | 通常不必标准化 | 通常不必 | **几乎必须标准化** |
| 解释 | 规则直观 | 重要性可看 | 边界几何强，规则不如树直观 |

---

## 二、硬间隔、软间隔与公式

### 2.1 线性判别

$$
f(x)=w^\top x+b
$$

希望正确分类且留出间隔，约束可写成：

$$
y_i(w^\top x_i+b)\ge 1
$$

（标签常取 $\pm 1$。）

### 2.2 硬间隔

必须完全分开，一个错都不能有。真实数据有噪声、重叠时：可能无解，或过拟合。

$$
\min_{w,b}\frac{1}{2}\|w\|^2
\quad\text{s.t.}\quad
y_i(w^\top x_i+b)\ge 1
$$

最大化间隔 $\Leftrightarrow$ 最小化 $\|w\|$（在上述约束下）。

### 2.3 软间隔（企业默认思路）

允许少量样本越界，用 **松弛变量 $\xi_i$** 记录违规程度，再用 $C$ 惩罚：

$$
\min_{w,b,\xi}\frac{1}{2}\|w\|^2 + C\sum_{i=1}^{n}\xi_i
\quad\text{s.t.}\quad
y_i(w^\top x_i+b)\ge 1-\xi_i,\ \xi_i\ge 0
$$

人话：一边把间隔撑大，一边控制犯错代价。**$C$ 就是两边的旋钮。**

---

## 三、控制台：`C`、核函数、`gamma`

### 3.1 参数 $C$（错误惩罚强度）

| $C$ | 行为 | 风险 |
| --- | --- | --- |
| 很小 | 宽容大局，关注整体泛化 | 易欠拟合 |
| 很大 | 零容忍，严惩错分 | 易过拟合、边界扭曲 |

业务举例：

- 医疗筛查：可能宁愿 $C$ 大一点，少漏诊  
- 流失预警：若误伤太多正常用户，可减小 $C$ 或改阈值  

### 3.2 核函数（kernel）

线性不可分时，把数据升到更高维再分。**核技巧**：不显式升维，只算高维内积。

| 核 | 适合 | 注意 |
| --- | --- | --- |
| `linear` | 大致线性可分、文本高维稀疏 | 快、相对好解释 |
| `poly` | 多项式关系 | 阶数高易过拟合 |
| `rbf` | 通用非线性（课件常用默认） | 要调 `C` 与 `gamma` |

### 3.3 参数 `gamma`（RBF 影响范围）

| `gamma` | 行为 |
| --- | --- |
| 很小 | 单样本影响范围大，边界更平滑、更「全局」 |
| 很大 | 单样本影响极局部，边界碎成小岛，易过拟合 |

`gamma='scale'` / `'auto'`：按特征方差或特征数自动定宽度；网格搜索也可试具体数值。

### 3.4 三参数速记表

| 参数 | 作用 | 大了 | 小了 |
| --- | --- | --- | --- |
| `kernel` | 边界形状 / 表达能力 | — | — |
| `C` | 错分惩罚 | 更贴训练、易过拟合 | 更平滑、易欠拟合 |
| `gamma` | RBF 局部性 | 更局部、更复杂 | 更整体、更平滑 |

---

## 四、工程要点（课件反复强调）

1. **必须标准化**：间隔和核都依赖距离 / 内积。用 `StandardScaler`。  
2. **必须 Pipeline**：把缩放和 `SVC` 绑在一起，避免训练/预测处理不一致，也方便 CV / 上线。  
3. **`stratify=y`**：划分时保持正负比例。  
4. **`probability=True`**：可出概率，但更慢；风控/阈值策略常用。  
5. **不平衡**：`class_weight='balanced'`、重采样、或调决策阈值。  
6. **企业四可**：可复现（种子）、可追踪（参数与数据版本）、可部署（Pipeline）、可监控（上线指标）。  

预处理对照：树模型通常不必标准化；**SVM / K-Means / PCA 都必须。**

---

## 五、案例地图 + 综合代码

| 案例 | 任务 | 要点 |
| --- | --- | --- |
| 客户流失 | 二分类 | RBF + Pipeline；看 P/R/F1/AUC |
| 垃圾邮件 | 二分类（文本思想简化） | 高维稀疏时线性核常够用 |
| 金融风控初筛 | 不平衡二分类 | `class_weight='balanced'`，盯 Recall |
| 工业质检 | 缺陷识别 | 标准化；少数类看 Recall |

### 代码：流失风格最小可跑版（逐行注释）

```python
import numpy as np  # 数值计算
import pandas as pd  # 表格
from sklearn.datasets import make_classification  # 造分类数据
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold  # 划分与搜参
from sklearn.preprocessing import StandardScaler  # 标准化
from sklearn.pipeline import Pipeline  # 流水线
from sklearn.svm import SVC  # 支持向量机
from sklearn.metrics import (  # 评估
    accuracy_score, precision_score, recall_score, f1_score,  # 点指标
    roc_auc_score, confusion_matrix, classification_report,  # AUC 与报告
)

X, y = make_classification(  # 模拟流失数据
    n_samples=2000,  # 样本数
    n_features=8,  # 特征数
    n_informative=5,  # 有用特征
    n_redundant=1,  # 冗余
    weights=[0.8, 0.2],  # 约 20% 正类（流失）
    random_state=42,  # 可复现
)
X = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])  # 列名

X_tr, X_te, y_tr, y_te = train_test_split(  # 划分
    X, y, test_size=0.3, random_state=42, stratify=y  # 分层
)

pipe = Pipeline([  # 标准化 + SVM 绑死
    ("scaler", StandardScaler()),  # 先缩放
    ("svc", SVC(  # 支持向量机
        kernel="rbf",  # 高斯核，非线性边界
        C=1.0,  # 惩罚强度
        gamma="scale",  # 自动宽度
        class_weight="balanced",  # 照顾少数类
        probability=True,  # 输出概率（更慢）
        random_state=42,  # 可复现
    )),
])
pipe.fit(X_tr, y_tr)  # 训练整条流水线

proba = pipe.predict_proba(X_te)[:, 1]  # 正类概率
pred = pipe.predict(X_te)  # 默认阈值硬分类

print("Accuracy :", round(accuracy_score(y_te, pred), 4))  # 准确率
print("Precision:", round(precision_score(y_te, pred), 4))  # 精确率
print("Recall   :", round(recall_score(y_te, pred), 4))  # 召回率
print("F1       :", round(f1_score(y_te, pred), 4))  # F1
print("AUC      :", round(roc_auc_score(y_te, proba), 4))  # 排序能力
print("混淆矩阵:\n", confusion_matrix(y_te, pred))  # [[TN FP],[FN TP]]
print(classification_report(y_te, pred, digits=4))  # 完整报告

# ---------- 可选：网格搜索 ----------
param_grid = {  # 搜索空间（演示用小网格）
    "svc__C": [0.5, 1, 2],  # 注意 Pipeline 参数前缀 svc__
    "svc__gamma": ["scale", 0.1, 0.01],  # gamma 候选
}
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)  # 分层 CV
gs = GridSearchCV(  # 网格搜索
    pipe,  # 同一条流水线
    param_grid=param_grid,  # 参数网格
    scoring="roc_auc",  # 以 AUC 选参
    cv=cv,  # 交叉验证
    n_jobs=-1,  # 并行
)
gs.fit(X_tr, y_tr)  # 搜参
print("最优参数:", gs.best_params_)  # 最佳组合
print("CV 最优 AUC:", round(gs.best_score_, 4))  # 交叉验证分数
```

**读结果**：先看 Recall / AUC（流失更怕漏）；再谈要不要降阈值做前置干预。支持向量个数可用 `pipe.named_steps["svc"].n_support_` 查看（需在未包概率的某些设定下更直观，理解「少数点撑边界」即可）。

---

## 六、易错点、自测、练习

### 6.1 易错点

1. 不做标准化就上 SVM。  
2. 测试集用另一套缩放，或训练/预测缩放不一致（没用 Pipeline）。  
3. 把 $C$ 和 `gamma` 调反直觉，只追训练集准确率。  
4. 不平衡只报 Accuracy。  
5. 样本量极大仍硬上复杂 RBF，不考虑线性核 / 近似。  
6. 以为所有训练点都同等重要（忽略支持向量）。  
7. 硬间隔思维对待噪声数据。  
8. 把 SVM 和「不必标准化的树模型」预处理混用。  

### 6.2 自测

1. 最大间隔为什么往往更好？  
2. 支持向量是哪些点？  
3. 硬间隔 vs 软间隔？  
4. $C$ 变大通常怎样？  
5. `gamma` 变大通常怎样？  
6. 为什么 SVM 必须标准化？  
7. Pipeline 解决什么？  

答案：离最近点更远更稳；撑住间隔边缘的点；完美分开 vs 允许越界并用 $C$ 惩罚；更严、易过拟合；更局部、边界更碎；依赖距离/内积；训练预测处理一致并便于 CV/上线。

### 6.3 练习

1. 同一数据对比 `linear` vs `rbf`。  
2. 去掉 `class_weight='balanced'`，观察 Recall。  
3. 扫决策阈值，画 Precision–Recall。  
4. 与随机森林对比：谁更稳、谁更好解释。  

---

## 七、公式与选型速查

$$
f(x)=w^\top x+b
$$

$$
\min\frac12\|w\|^2+C\sum_i\xi_i
\quad\text{s.t.}\quad
y_i(w^\top x_i+b)\ge 1-\xi_i
$$

**什么时候想到 SVM？** 有标签、要预测类别、中小规模/高维、需要清晰决策边界。

**和两姊妹篇：** 没标签分群 → K-Means；高维冗余/可视化 → PCA；常组合 **PCA + SVM**（先压缩再分类，但不保证准确率一定升）。

---

## 八、一句话收束

> SVM 用最大间隔找最稳健的分类边界，支持向量决定「公路」宽度；工程上标准化 + Pipeline + 合理的 $C$/核/`gamma`，再配上不平衡策略，才能从课件公式走到企业流失/风控/质检场景。

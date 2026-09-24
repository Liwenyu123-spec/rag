# PCA 详细复习笔记

> 材料：`SVM_Kmeans_PCA导引课.html`、课件、`昨今两日讲义详细汇总`，以及 **9月7日上午课**（正交=协方差为0、累积85%、PCA→K-Means→SVM 流水线）。  
> 写法：直觉 → 几何/代数 → 公式 → 选维与载荷 → 三件套流水线 → 逐行注释代码。  
> 公式：`$...$` / `$$...$$`（Typora 0.94）。  
> 姊妹篇：`SVM详细复习笔记.md`、`K-Means详细复习笔记.md`。

---

## 〇、这份笔记怎么用

总览一句话：

> **PCA 解决高维冗余：把坐标轴旋转到「方差最大」的方向，再投影压缩，便于可视化、降噪与下游建模。**

选型定位：

| 维度 | PCA |
| --- | --- |
| 标签 | **无标签**（不看 $y$） |
| 业务痛点 | 消除高维度数据冗余 |
| 视觉隐喻 | 捕捉最大方差的投影光源 |
| 核心输出 | 降维后的主成分坐标 + 解释方差 + 载荷 |

| 章 | 内容 |
| --- | --- |
| 一 | 降维动机与「不是删列」 |
| 二 | 几何视角：旋转坐标系与正交 |
| 三 | 代数视角：正交 = 协方差为 0；特征值/SVD |
| 四 | 解释方差比、载荷、选维（课标 ≥85%） |
| 五 | PCA vs 特征选择；PCA→K-Means→SVM 流水线 |
| 六 | 综合代码（含完整流水线）、易错点、自测 |

```python
# pip install scikit-learn pandas numpy matplotlib
```

---

## 一、降维在解决什么

### 1.1 什么是「维」

维度 ≈ 特征个数。特征太多时常见问题：

- 计算变贵、模型更不稳  
- 特征互相冗余（共线）  
- 噪声多  
- 人眼无法直接看高维结构  

### 1.2 PCA 不是简单删列

PCA **不是**「删掉不重要的原始列」那么粗暴，而是：

> 找一组新的坐标轴（重要方向），把数据投影到这些轴上。

新坐标 = 原始特征的 **线性组合**。

企业用途：高维可视化、降噪、加快下游模型、缓解多重共线、压缩传感器 / 图像 / 金融因子。

### 1.3 术语卡

| 术语 | 人话 |
| --- | --- |
| 方差 | 沿某方向散得开不开 |
| 协方差 | 两特征是否一起变 |
| 协方差矩阵 | 各方差与两两协方差的表 |
| 主成分 PC | 新轴：方差最大的方向们 |
| 解释方差比 | 每个 PC 占总方差比例 |
| 载荷 loadings | 原始特征在某 PC 上的权重 |
| 累计方差 | 前几个 PC 一共保留多少信息 |

---

## 二、几何视角：旋转坐标系与正交（9月7日课）

### 2.1 不是删列，是旋转找「影子最大」的方向

课上类比：**拍照找最佳角度**——旋转坐标系，让数据投影的「影子」面积最大。  
那个方向 = **PC1**；方差最大 ≈ 信息最多 ≈ 最能拉开样本。

### 2.2 为什么要正交

| 主成分 | 含义 |
| --- | --- |
| PC1 | 方差最大方向 |
| PC2 | 与 PC1 **正交**，剩余里方差最大 |
| PC3 | 与前两者都正交，再取最大…… |

不正交 → 轴之间有夹角 → **信息重叠、冗余**。  
正交 → 彼此独立携带信息。

### 2.3 为何最大化方差

散得开的方向往往更有区分信息。  
注意：这是 **无监督** 标准，**不等于**「对分类最有用的方向」。

主成分例子（示意）：

$$
z_1 = 0.62x_1 + 0.51x_2 + 0.59x_3
$$

业务含义靠 **载荷** 翻译，不是拍脑袋。

---

## 三、代数视角：正交 = 协方差为 0

### 3.1 课上必背对应

> **几何上的正交 ⇔ 代数上主成分之间协方差为 0 ⇔ 主成分互不相关。**

由此消掉原始特征里的共线冗余。

协方差符号直觉：

| 协方差 | 含义 |
| --- | --- |
| 大于 0 | 同向变 |
| 小于 0 | 反向变 |
| 等于 0 | 不一起变（不相关） |

### 3.2 协方差矩阵与特征分解

- 对角：各特征方差；非对角：两两协方差  
- 点云若是斜椭圆，**PC1 ≈ 长轴**  

在 $\|w\|=1$ 下最大化投影方差：

$$
\max_w\ w^\top \Sigma w \quad\text{s.t.}\quad w^\top w=1
\quad\Leftrightarrow\quad
\Sigma w = \lambda w
$$

| 对象 | 含义 |
| --- | --- |
| 特征向量 $w$ | 主成分方向 |
| 特征值 $\lambda$ | 该方向上的方差（信息量） |

按 $\lambda$ 从大到小排序 → PC1, PC2, …

### 3.3 SVD（知道即可）

也可对数据矩阵做 **SVD** 算主成分；大规模时往往更稳。sklearn `PCA` 底层常用相关数值方法，你调 `fit/transform` 即可。

### 3.4 企业标准流程

明确目标 → 数值特征清洗 → **必须标准化** → 拟合 PCA → 看累计方差 / 载荷 → `transform` → Pipeline 锁死上线。

---

## 四、解释方差比、载荷、选几个（课标 ≥85%）

### 4.1 可解释方差比

$$
\text{第 }k\text{ 个 PC 的解释方差比}=\frac{\lambda_k}{\sum_j\lambda_j}
$$

sklearn：`explained_variance_ratio_`；累计：`np.cumsum(...)`。

### 4.2 课上判断线

> 累积可解释方差比通常要求 **> 85%**，再用这 $k$ 个主成分替代原特征。

也可 `PCA(n_components=0.85)` 让算法自动留到 85%。  
工程上还会结合下游效果试 0.8 / 0.9 / 0.95。

例：100 维 → PC1～PC4 累计 90% → 压掉 96% 维数仍留九成信息。

### 4.3 载荷

原始特征在某 PC 上的权重；把「PC1」翻成业务话：

> PC1 主要由负载、扭矩、电流、温度构成 → 「负载-能耗-热状态」综合轴。

### 4.4 关键提醒

> **PCA 最大化的是方差，不是分类准确率。** 接 SVM 不一定分数更高，但常更快、更稳、更抗冗余。

---

## 五、PCA vs 特征选择；三件套流水线

### 5.1 PCA（特征提取）vs 特征选择

| | PCA | 特征选择 |
| --- | --- | --- |
| 得到什么 | 原始特征的线性组合（主成分） | 仍是原始列 |
| 可解释性 | 较差，靠载荷翻译 | 较好 |
| 信息 | 按方差尽量保留 | 可能误删有用列 |

### 5.2 课上组合拳：滤网 → 探索 → 分类

```text
高维数据
  →【PCA】滤网：降维去噪、消冗余
  →【K-Means】在低维空间探索自然结构 → 技术标签（簇号）
  →【人工复核】技术标签 → 业务标签（高价值/流失风险…）
  →【SVM】有监督分类，服务新样本
```

| 角色 | 监督？ | 干什么 |
| --- | --- | --- |
| PCA | 无 | 滤网 |
| K-Means | 无 | 探索结构 |
| SVM | 有 | 最终分类 |

新数据：**同一套** `scaler → pca.transform → svm.predict`（不要重新 fit）。

### 5.3 其他组合提醒

- PCA 画 2D 很好；**只在 2 维里聚类**可能失真，要有意识  
- 传感器高维压缩：标准化 → 累计方差图 → 载荷命名 → 再下游  

### 5.4 优缺点

**优点**：压缩、去冗余、可视化、降噪。  
**缺点**：不如原特征好懂；不一定抬高监督指标；怕尺度；线性方法。

---

## 六、综合代码（逐行注释）

### 6.1 累计方差（课标 85%）+ 载荷 + PCA↔SVM 对照

```python
import numpy as np  # 数值计算
import pandas as pd  # 表格
import matplotlib.pyplot as plt  # 画解释方差
from sklearn.datasets import make_classification  # 造高维相关特征
from sklearn.preprocessing import StandardScaler  # 标准化
from sklearn.decomposition import PCA  # 主成分
from sklearn.model_selection import train_test_split  # 划分
from sklearn.pipeline import Pipeline  # 流水线
from sklearn.svm import LinearSVC  # 线性 SVM 做对照
from sklearn.metrics import accuracy_score  # 准确率

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]  # 中文
plt.rcParams["axes.unicode_minus"] = False  # 负号

X, y = make_classification(  # 高维分类数据
    n_samples=1000, n_features=20, n_informative=6,  # 真正有用较少
    n_redundant=10, random_state=42,  # 大量冗余（适合 PCA）
)
feat_names = [f"x{i}" for i in range(X.shape[1])]  # 特征名
df = pd.DataFrame(X, columns=feat_names)  # 表

scaler = StandardScaler()  # 标准化（必须）
Xs = scaler.fit_transform(df)  # 缩放

pca_full = PCA(random_state=42)  # 先看全部成分方差
pca_full.fit(Xs)  # 拟合
ratio = pca_full.explained_variance_ratio_  # 各 PC 占比
cum = np.cumsum(ratio)  # 累计
n85 = int(np.argmax(cum >= 0.85) + 1)  # 课标：累计 ≥85%
print("累积≥85%需要主成分数:", n85, "降维比:", round((1 - n85 / X.shape[1]) * 100, 1), "%")  # 打印

plt.figure(figsize=(8, 4))  # 画布
plt.plot(range(1, len(cum) + 1), cum, marker="o")  # 累计曲线
plt.axhline(0.85, color="green", linestyle="--", label="85%课标")  # 课标线
plt.axvline(n85, color="blue", linestyle="--", label=f"{n85}个达标")  # 维数
plt.xlabel("主成分个数")  # x
plt.ylabel("累计解释方差比")  # y
plt.title("选多少维：看累计方差")  # 标题
plt.legend()  # 图例
plt.grid(True, alpha=0.3)  # 网格
plt.show()  # 显示

pca = PCA(n_components=n85, random_state=42)  # 按课标维数降维
Z = pca.fit_transform(Xs)  # 投影
loadings = pd.DataFrame(  # 载荷表
    pca.components_.T, index=feat_names,  # 特征 x PC
    columns=[f"PC{i+1}" for i in range(n85)],  # 列名
)
print("PC1 载荷 |abs| Top5:\n", loadings["PC1"].abs().sort_values(ascending=False).head())  # 解释 PC1

X_tr, X_te, y_tr, y_te = train_test_split(df, y, test_size=0.3, random_state=42, stratify=y)  # 划分
pipe_raw = Pipeline([("scaler", StandardScaler()), ("clf", LinearSVC(max_iter=5000, random_state=42))])  # 原特征
pipe_pca = Pipeline([  # PCA+SVM
    ("scaler", StandardScaler()),  # 缩放
    ("pca", PCA(n_components=0.85, random_state=42)),  # 自动留到 85%
    ("clf", LinearSVC(max_iter=5000, random_state=42)),  # 分类
])
pipe_raw.fit(X_tr, y_tr)  # 训练
pipe_pca.fit(X_tr, y_tr)  # 训练
print("原特征 Acc:", round(accuracy_score(y_te, pipe_raw.predict(X_te)), 4))  # 对照
print("PCA(85%)+SVM Acc:", round(accuracy_score(y_te, pipe_pca.predict(X_te)), 4),  # 对照
      "维数:", pipe_pca.named_steps["pca"].n_components_)  # 实际维数
```

### 6.2 课上完整流水线：PCA → K-Means →（业务标签）→ SVM

```python
import numpy as np  # 数值
from sklearn.datasets import make_blobs  # 造无标签团块
from sklearn.preprocessing import StandardScaler  # 标准化
from sklearn.decomposition import PCA  # 滤网
from sklearn.cluster import KMeans  # 探索
from sklearn.model_selection import train_test_split  # 划分
from sklearn.svm import SVC  # 监督分类
from sklearn.metrics import classification_report  # 报告

rng = np.random.RandomState(42)  # 种子
# 模拟「无标签高维数据」：先有结构，再人为加冗余维
X_core, tech = make_blobs(n_samples=600, centers=4, n_features=6, cluster_std=1.2, random_state=42)  # 核心结构
noise = rng.normal(0, 1, size=(600, 14))  # 噪声/冗余维
X_unlabeled = np.hstack([X_core, noise])  # 凑成 20 维「海量特征」
new_data = X_unlabeled[:5].copy()  # 假装新样本

# ----- 阶段1：无监督探索 -----
scaler = StandardScaler()  # 缩放器
Xs = scaler.fit_transform(X_unlabeled)  # 只在无标签池上 fit
pca = PCA(n_components=0.85, random_state=42)  # 滤网：留 85% 方差
Xp = pca.fit_transform(Xs)  # 降维
print("PCA:", X_unlabeled.shape[1], "→", Xp.shape[1])  # 维数变化

kmeans = KMeans(n_clusters=4, init="k-means++", n_init=10, random_state=42)  # 探索
cluster_id = kmeans.fit_predict(Xp)  # 技术标签 = 簇号
print("各簇人数:", np.bincount(cluster_id))  # 分布

# ----- 阶段2：技术标签 → 业务标签（真实项目要人工看质心/画像） -----
business_map = {0: "低价值", 1: "中价值", 2: "高价值", 3: "流失风险"}  # 人工命名示意
y_biz = np.array([business_map[c] for c in cluster_id])  # 业务标签

# ----- 阶段3：SVM 监督分类（在 PCA 空间上） -----
X_tr, X_te, y_tr, y_te = train_test_split(  # 划分
    Xp, y_biz, test_size=0.2, random_state=42, stratify=y_biz  # 分层
)
svm = SVC(C=10, kernel="rbf", gamma="scale", random_state=42)  # SVM
svm.fit(X_tr, y_tr)  # 训练
print(classification_report(y_te, svm.predict(X_te)))  # 评估

# ----- 阶段4：新数据必须走同一套 transform -----
new_pred = svm.predict(pca.transform(scaler.transform(new_data)))  # scaler→pca→svm
print("新样本预测:", new_pred)  # 业务类名
```

**读结果**：先看累计方差是否过 85%；流水线里 PCA 是滤网、K-Means 出技术标签、人工换成业务名、SVM 服务增量预测。

---

## 七、易错点、自测、练习

### 7.1 易错点

1. 不标准化就 PCA。  
2. 以为 PCA 一定提高分类准确率。  
3. 把主成分直接当原始业务指标，不做载荷解读。  
4. 只保留 2 维就聚类还不验证。  
5. 训练/预测 PCA 变换不一致（没用同一 scaler/pca）。  
6. 忘记「正交 ⇔ 协方差为 0」。  
7. 对非线性流形硬指望 PCA。  

### 7.2 自测

1. PCA 要不要标签？  
2. 正交在代数上对应什么？  
3. 特征向量 / 特征值各是什么？  
4. 课上累积方差常用阈值？  
5. 流水线里 PCA / K-Means / SVM 各扮演什么？  
6. PCA 一定提升 SVM 吗？  

答案：不要；协方差为 0；方向 / 该方向方差；约 85%；滤网 / 探索技术标签 / 监督分类；不一定。

### 7.3 练习

1. 用载荷给 PC1 起业务名。  
2. 对比 `n_components=0.8/0.85/0.95` 下游表现。  
3. 空手画：PCA→K-Means→人工命名→SVM→新样本预测。  

---

## 八、三件套选型（总览收官）

| 问题 | 更倾向 |
| --- | --- |
| 有没有标签？ | 有 → SVM；无 → K-Means 或 PCA |
| 分组 / 预测 / 压缩？ | K-Means / SVM / PCA |
| 高维难啃？ | 先 PCA 滤网 |

预处理：SVM、K-Means、PCA **都要标准化**。

---

## 九、公式速查

$$
\max_{\|w\|=1}w^\top\Sigma w
\quad\Leftrightarrow\quad
\Sigma w=\lambda w
$$

$$
\text{解释方差比}_k=\frac{\lambda_k}{\sum_j\lambda_j},\quad
\text{课标：累计}>85\%
$$

$$
z_1 = a_1 x_1 + a_2 x_2 + \dots + a_p x_p
$$

（$a_i$ 与载荷相关。）

---

## 十、一句话收束

> PCA 把坐标轴旋到方差最大且彼此正交（协方差为 0）的方向再投影；用累计 ≥85% 选维，用载荷做业务翻译，再用「PCA 滤网 → K-Means 探索 → SVM 分类」把无监督接到有监督上。

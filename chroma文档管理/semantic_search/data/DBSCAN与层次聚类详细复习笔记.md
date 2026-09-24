# DBSCAN与层次聚类详细复习笔记

> 电脑里原先主要有 K-Means；本篇补另外两条常用聚类路线。  
> 姊妹篇：K-Means、PCA、特征工程、机器学习基础与模型评估。  
> 公式：`$...$` / `$$...$$`。

---

## 〇、一句话抓住全篇

> **K-Means 切「球状团」；DBSCAN 按密度连片，能抓不规则形状并标噪声；层次聚类用树状图看多粒度合并/分裂。**

| 章 | 内容 |
| --- | --- |
| 一 | 三者选型地图 |
| 二 | DBSCAN |
| 三 | 层次聚类 |
| 四 | 评估与预处理 |
| 五 | 代码 |
| 六 | 易错点与自测 |

```python
# pip install scikit-learn pandas numpy matplotlib
```

---

## 一、和 K-Means 怎么选

| | K-Means | DBSCAN | 层次聚类 |
| --- | --- | --- | --- |
| 要预设 $K$？ | 要 | 不要（间接由密度参数定） | 可后切树定簇数 |
| 形状 | 偏球形 | 任意形状密度连通 | 取决于链接方式 |
| 噪声 | 强行分进某簇 | 可标为噪声 $-1$ | 一般强行进树 |
| 规模 | 大样本友好 | 中小更常见 | 大样本慢 |
| 尺度 | **必须标准化** | **必须** | **必须** |

无标签 → 无监督；评估用轮廓系数等，或看业务可解释性。

---

## 二、DBSCAN

### 2.1 核心直觉

- **邻域半径** `eps`：多近算「旁边」  
- **最少点数** `min_samples`：邻域里至少多少点才算密集  

点类型：

| 类型 | 含义 |
| --- | --- |
| 核心点 | 邻域内点数 $\ge$ `min_samples` |
| 边界点 | 自己不够密，但落在某核心点邻域 |
| 噪声 | 谁也不靠，标为 `-1` |

算法：从核心点出发，把密度可达的点收成一簇。

### 2.2 调参直觉

| 现象 | 可能原因 |
| --- | --- |
| 几乎全是噪声 | `eps` 太小或 `min_samples` 太大 |
| 全并成一簇 | `eps` 太大 |
| 簇碎一堆 | `eps` 略小 |

可用 k-距离图辅助选 `eps`（把每点到第 $k$ 近邻距离排序看拐肘）。

### 2.3 优缺点

优点：不规则形状、自动发现簇数、抗噪声。  
缺点：密度差异悬殊时难受；高维距离失效（可先 PCA）；参数敏感。

---

## 三、层次聚类

### 3.1 凝聚式（最常用）

自下而上：每点先各算一簇，不断合并「最近」的两簇，直到结束。  
用 **树状图（dendrogram）** 看合并历史，横切一刀得到簇。

### 3.2 链接方式 linkage

| linkage | 簇间距离怎么定义 |
| --- | --- |
| `ward` | 合并后增加的方差（偏球状，常用） |
| `average` | 两簇点对平均距离 |
| `complete` | 最远点对 |
| `single` | 最近点对（易链式粘连） |

sklearn：`AgglomerativeClustering`；画树可用 `scipy.cluster.hierarchy`。

### 3.3 何时用

要「粗分/细分都能看」的谱系、样本量不太大、需要可解释的合并过程。

---

## 四、预处理与简单评估

1. **StandardScaler**（或稳健缩放）几乎必做。  
2. 高维可先 **PCA** 到 2～20 维再聚类（解释时要声明信息损失）。  
3. 轮廓系数 `silhouette_score`：越接近 1 越好；DBSCAN 算轮廓时通常 **先去掉噪声点**。  
4. 业务验收：簇是否好命名、好运营（比分数更重要）。

---

## 五、综合代码（逐行注释）

```python
import numpy as np  # 数值
import matplotlib.pyplot as plt  # 图
from sklearn.datasets import make_moons, make_blobs  # 造不规则与团块
from sklearn.preprocessing import StandardScaler  # 标准化
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering  # 三种聚类
from sklearn.metrics import silhouette_score  # 轮廓系数
from scipy.cluster.hierarchy import linkage, dendrogram  # 树状图

# ---------- 月牙数据：K-Means 易失败，DBSCAN 擅长 ----------
X_moon, y_moon = make_moons(n_samples=600, noise=0.08, random_state=42)  # 两弯月
X_moon = StandardScaler().fit_transform(X_moon)  # 缩放

km = KMeans(n_clusters=2, random_state=42, n_init=10).fit_predict(X_moon)  # K-Means
db = DBSCAN(eps=0.25, min_samples=5).fit_predict(X_moon)  # DBSCAN
print("DBSCAN 噪声点数:", int(np.sum(db == -1)))  # 噪声

# ---------- 层次聚类 + 树状图（用团块数据更清晰） ----------
X_blob, _ = make_blobs(n_samples=120, centers=3, cluster_std=0.8, random_state=42)  # 三团
X_blob = StandardScaler().fit_transform(X_blob)  # 缩放
Z = linkage(X_blob, method="ward")  # 凝聚过程矩阵
plt.figure(figsize=(8, 4))  # 画布
dendrogram(Z, truncate_mode="level", p=5)  # 树状图（截断层级便于看）
plt.title("层次聚类树状图（Ward）")  # 标题
plt.xlabel("样本或簇")  # x
plt.ylabel("距离")  # y
plt.tight_layout()  # 布局
plt.show()  # 显示

agg = AgglomerativeClustering(n_clusters=3, linkage="ward")  # 切成 3 簇
labels_agg = agg.fit_predict(X_blob)  # 预测
print("层次轮廓:", round(silhouette_score(X_blob, labels_agg), 4))  # 评估

# DBSCAN 轮廓：排除噪声
mask = db != -1  # 非噪声
if mask.sum() > 0 and len(set(db[mask])) > 1:  # 至少两簇
    print("DBSCAN 轮廓(去噪声):", round(silhouette_score(X_moon[mask], db[mask]), 4))  # 分数
print("KMeans 轮廓(月牙):", round(silhouette_score(X_moon, km), 4))  # 往往一般
```

---

## 六、易错点与自测

1. 不标准化就跑密度/距离聚类。  
2. 把 DBSCAN 的 `-1` 当成普通簇 ID 去算业务均值。  
3. 密度差很大仍死调一组 `eps`。  
4. 上万点硬画完整 dendrogram 又慢又糊。  
5. 只凭轮廓系数否定业务上清晰的噪声分离。  

自测：DBSCAN 两个关键参数？噪声标签？Ward 层次适合什么形状？相对 K-Means 最大卖点？  
答案：`eps`/`min_samples`；`-1`；偏球状团；不规则形状+噪声。

---

## 七、一句话收束

> 聚类不止 K-Means：形状怪、有噪声想 DBSCAN；要谱系、要多粒度想层次聚类；无论哪种，先缩放，再用指标 + 业务叙事一起验收。

# K-Means 详细复习笔记

> 材料：`SVM_Kmeans_PCA导引课.html`、`SVM_Kmeans_PCA_总览.pdf`、`SVM_Kmeans_PCA_课件.md`，以及《昨今两日讲义详细汇总》。  
> 写法对齐《集成学习详细笔记》：直觉 → 公式 → 选 K → 画像落地 → 逐行注释代码 → 自测。  
> 公式：`$...$` / `$$...$$`（Typora 0.94）。  
> 姊妹篇：`SVM详细复习笔记.md`、`PCA详细复习笔记.md`。

---

## 〇、这份笔记怎么用

总览一句话：

> **K-Means 解决无监督分群：按距离把样本吸到若干「星团中心」，探索天然相似性。**

选型定位：

| 维度 | K-Means |
| --- | --- |
| 标签 | **无标签** |
| 业务痛点 | 探索天然的相似性分群 |
| 视觉隐喻 | 引力汇聚的星团中心 |
| 核心输出 | 所属簇编号 + 簇中心 |

| 章 | 内容 |
| --- | --- |
| 一 | 无监督、距离、簇不是真理 |
| 二 | 四步迭代与目标函数 |
| 三 | 选 K、标准化、局限 |
| 四 | 用户/门店案例与 10 步流程 |
| 五 | 综合代码 |
| 六 | 易错点、自测、与 SVM/PCA 组合 |

```python
# pip install scikit-learn pandas numpy matplotlib
```

---

## 一、无监督与聚类直觉

### 1.1 监督 vs 无监督

| | 监督学习 | 无监督学习 |
| --- | --- | --- |
| 标签 | 有 $y$ | 没有 $y$ |
| 目标 | 学 $x\to y$ | 找数据结构 |
| 代表 | SVM、逻辑回归、树 | K-Means、PCA |

**聚类（Clustering）**：按「相似」分组。默认常用 **欧氏距离**。

### 1.2 关键警告（课件反复讲）

聚类结果 **不是天然真理**：

- 换特征、换 $K$、换距离，群会变  
- 必须做 **簇画像**，用业务语言命名，才能落地运营  

企业场景：用户分层、门店分群、设备工况模式、营销策略分层。

### 1.3 术语卡

| 术语 | 人话 |
| --- | --- |
| 簇 / Cluster | 分出来的一组 |
| 簇中心 / Centroid | 该组的「代表点」，常取均值 |
| $K$ | 你要分几组 |
| Assignment | 每个点归最近中心 |
| Update | 中心改成组内均值 |
| WCSS / Inertia | 组内平方距离总和，`inertia_` |
| 轮廓系数 | 离自己簇近、离别簇远的程度 |
| 簇画像 | 用均值/分布描述每簇业务模样 |

---

## 二、算法在干什么

### 2.1 一句话

指定 $K$ 个中心，让 **组内尽量紧、组间尽量分**。

### 2.2 纳米级四步（「搬桌子」）

1. **初始化簇中心**（敏感；sklearn 默认常 `k-means++`，比纯随机稳）  
2. **Assignment**：每个样本归到最近中心  
3. **Update**：每个簇中心改成该簇样本均值  
4. 重复直到中心几乎不动，或达到 `max_iter`  

为什么更新取均值：在欧氏平方距离下，均值正是让簇内平方和最小的点。

### 2.3 目标函数 WCSS

**WCSS / Inertia / SSE** = 所有样本到各自簇中心的平方距离总和。

$$
\min_{C_1,\dots,C_K,\,\mu_1,\dots,\mu_K}
\sum_{k=1}^{K}\sum_{x_i\in C_k}\|x_i-\mu_k\|^2
$$

- 越小 → 簇内越紧  
- **但 $K$ 越大，WCSS 几乎一定下降**，所以不能只看「最小就最好」  

sklearn：`model.inertia_`。

---

## 三、怎么选 $K$、为什么必须标准化

### 3.1 选 $K$ 的两板斧 + 业务

| 方法 | 做法 | 注意 |
| --- | --- | --- |
| 肘部法则 Elbow | 画 $K$–WCSS，找下降变缓的肘点 | 肘点有时不明显 |
| 轮廓系数 Silhouette | 越接近 1 越好 | 结合可解释性 |
| 业务可执行性 | 运营能否撑住这么多策略 | 常常是最终约束 |

太小：不同模式搅在一起。太大：运营无法执行。

### 3.2 必须标准化

金额、次数、天数可能差几个数量级。不标准化 → 大数值特征绑架距离 → 分群失真。

K-Means 还对 **异常值敏感**，并较适合较「球状」的簇；月牙形、条带形可能吃力。

### 3.3 优缺点

**优点**：简单高效、可解释、分层起点好。  
**缺点**：要预先指定 $K$；对初始化/异常值/尺度敏感；非球状簇差。

---

## 四、案例与企业 10 步

### 4.1 案例：电商用户分层（RFM 思路）

特征直觉：最近一次消费、频率、金额，再加客单价、用券率、退货率、App 活跃天数等。

流程：标准化 → 肘部图 + 轮廓系数 → 选定 $K$（课件常演示 4）→ 按簇统计均值做画像 → 2D/3D 看是否分开 → 命名并定策略。

### 4.2 案例：门店经营类型

课件示例画像方向：

| 簇方向 | 策略直觉 |
| --- | --- |
| 高客流高转化 | 爆款陈列、高峰排班 |
| 社区稳定复购 | 会员运营、复购活动 |
| 高客单低客流 | 高客单服务、预约 |
| 促销依赖型 | 促销节奏与成本控制 |

### 4.3 企业级 10 步

1. 业务目标明确（分群为了运营，不是为了聚类本身）  
2. 特征准备  
3. 清洗  
4. **标准化**  
5. 选 $K$  
6. 训练  
7. 簇画像  
8. 起业务名  
9. 定策略  
10. 持续监控（客群结构会漂）  

### 4.4 和 PCA / SVM 怎么搭

- **PCA + K-Means**：PCA 常用来 **2D 展示**；聚类更建议在标准化后的原始（或适度降维）空间做，避免只在投影空间聚类失真。  
- **K-Means + SVM**：先分群探索，人工/规则命名后再用 SVM 做「新样本归群」的监督模型。  

---

## 五、综合代码（逐行注释）

```python
import numpy as np  # 数值计算
import pandas as pd  # 表格与画像
import matplotlib.pyplot as plt  # 肘部图
from sklearn.datasets import make_blobs  # 造团状数据
from sklearn.preprocessing import StandardScaler  # 标准化
from sklearn.cluster import KMeans  # K-Means
from sklearn.metrics import silhouette_score  # 轮廓系数

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]  # 中文
plt.rcParams["axes.unicode_minus"] = False  # 负号

X, y_true = make_blobs(  # 模拟用户特征团
    n_samples=800,  # 样本
    n_features=4,  # 4 个特征，如 R/F/M/活跃
    centers=4,  # 潜在 4 群
    cluster_std=1.2,  # 簇内离散
    random_state=42,  # 可复现
)
cols = ["recency", "frequency", "monetary", "active_days"]  # 假装业务列名
df = pd.DataFrame(X, columns=cols)  # 特征表

scaler = StandardScaler()  # 标准化器
Xs = scaler.fit_transform(df)  # 拟合并转换

inertias = []  # 存 WCSS
silhouettes = []  # 存轮廓系数
Ks = range(2, 9)  # 候选 K
for k in Ks:  # 扫 K
    km = KMeans(n_clusters=k, n_init=10, random_state=42)  # k-means++
    labels = km.fit_predict(Xs)  # 训练并得到标签
    inertias.append(km.inertia_)  # WCSS
    silhouettes.append(silhouette_score(Xs, labels))  # 轮廓

fig, ax = plt.subplots(1, 2, figsize=(10, 4))  # 两张图
ax[0].plot(list(Ks), inertias, marker="o")  # 肘部图
ax[0].set_title("肘部法则：K vs WCSS")  # 标题
ax[0].set_xlabel("K")  # x
ax[0].set_ylabel("Inertia")  # y
ax[1].plot(list(Ks), silhouettes, marker="o", color="orange")  # 轮廓
ax[1].set_title("轮廓系数（越大越好）")  # 标题
ax[1].set_xlabel("K")  # x
ax[1].set_ylabel("Silhouette")  # y
plt.tight_layout()  # 布局
plt.show()  # 显示：结合肘点与轮廓选 K

best_k = 4  # 课件常用示例；实际应看图+业务
model = KMeans(n_clusters=best_k, n_init=10, random_state=42)  # 最终模型
df["cluster"] = model.fit_predict(Xs)  # 写入簇编号

profile = df.groupby("cluster")[cols].mean().round(3)  # 簇画像：各特征均值
print("簇画像（标准化前尺度的原始特征均值）:\n", profile)  # 解释用
print("各簇人数:\n", df["cluster"].value_counts().sort_index())  # 规模
print("中心（标准化空间）:\n", np.round(model.cluster_centers_, 3))  # 中心坐标

# 业务命名示例（需按画像改名字，不要照搬）
name_map = {  # 示例映射
    0: "高价值活跃",  # 举例
    1: "价格敏感",  # 举例
    2: "稳定成长",  # 举例
    3: "沉睡低活",  # 举例
}
df["segment"] = df["cluster"].map(name_map)  # 业务名
print(df["segment"].value_counts())  # 分层人数
```

**读结果**：先看人数是否极端不均；再看画像均值差异是否说得通；最后才定运营动作。

---

## 六、易错点、自测、练习

### 6.1 易错点

1. 不标准化。  
2. 只看 WCSS 最小选超大 $K$。  
3. 把簇编号当成「天然标签」不画像。  
4. 忽略异常值对中心的拉动。  
5. 对非球状结构硬上 K-Means。  
6. 初始化不固定导致结果乱跳（要设 `random_state`，并 `n_init` 足够）。  
7. 用 PCA 投影后的 2 维直接当唯一聚类空间还不验证。  

### 6.2 自测

1. K-Means 有没有标签？输出是什么？  
2. 四步迭代是什么？  
3. 为什么 Update 用均值？  
4. WCSS 随 $K$ 增大一定怎样？说明什么？  
5. 肘部法则和轮廓系数各看什么？  
6. 为什么必须标准化？  

答案：无标签，簇编号；初始化-分配-更新-重复；欧氏平方下均值最优；下降，故不能只看最小；缓降肘点 / 近1更好；大量纲会主导距离。

### 6.3 练习

1. 对真实一点的 RFM 表做分群并写四句运营策略。  
2. 对比 `n_init=1` 与 `n_init=10` 的稳定性。  
3. 加几个极端异常值，看中心如何被拽偏。  
4. 用 PCA 把结果画成 2D 着色（聚类仍在原标准化空间）。  

---

## 七、公式速查

$$
\sum_{k=1}^{K}\sum_{x_i\in C_k}\|x_i-\mu_k\|^2
$$

**什么时候想到 K-Means？** 没标签、要分层/分群、需要可执行的群划分、簇大致球状。

---

## 八、一句话收束

> K-Means 用「近谁归谁、中心取均值」把无标签数据分成 $K$ 团；标准化、选 $K$、簇画像和业务命名缺一不可，否则只是一串没有运营意义的簇编号。

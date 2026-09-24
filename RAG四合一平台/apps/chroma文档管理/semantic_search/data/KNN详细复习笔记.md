# KNN 详细复习笔记

> 材料：KNN 思维导图 / 知识体系、机器学习阶段测试（KNN 部分）、集成学习前置课。  
> 写法对齐既有详细笔记：直觉 → 流程 → 参数 → 代码（逐行注释）→ 易错点 → 自测。  
> 公式：`$...$` / `$$...$$`。  
> 姊妹篇：线性/逻辑回归、决策树、SVM、集成学习等。

---

## 〇、一句话抓住全篇

> **KNN：不训练复杂公式，预测时找最近的 $K$ 个邻居——分类投票，回归取平均。**

| 章 | 内容 |
| --- | --- |
| 一 | 思想、懒惰学习 |
| 二 | 距离与标准化 |
| 三 | $K$、权重、分类/回归 |
| 四 | 推荐召回与局限 |
| 五 | 综合代码 |
| 六 | 易错点与自测 |

```python
# pip install scikit-learn pandas numpy matplotlib
```

---

## 一、核心思想

### 1.1 人话

「近朱者赤」：新样本像谁，就跟谁一类（或取邻居目标的平均）。

### 1.2 懒惰学习（Lazy Learning）

| 阶段 | KNN 做什么 |
| --- | --- |
| 训练 | 基本只**存数据**（几乎不学参数） |
| 预测 | 才算距离、找邻居、投票/平均 |

对比：线性回归/逻辑回归/SVM/树会在训练阶段学出模型参数。

### 1.3 能做什么

| 任务 | 做法 | sklearn |
| --- | --- | --- |
| 分类 | 邻居多数投票 | `KNeighborsClassifier` |
| 回归 | 邻居目标平均（可加权） | `KNeighborsRegressor` |
| 相似检索 | 找最近邻商品/用户 | `NearestNeighbors` |

---

## 二、距离与必须标准化

### 2.1 常用距离

欧氏距离（最常见，$p=2$）：

$$
d(x,z)=\sqrt{\sum_{j=1}^{p}(x_j-z_j)^2}
$$

曼哈顿距离（$p=1$）：

$$
d(x,z)=\sum_{j=1}^{p}|x_j-z_j|
$$

Minkowski 距离统一形式：

$$
d(x,z)=\Big(\sum_{j=1}^{p}|x_j-z_j|^p\Big)^{1/p}
$$

课件口径：Minkowski 在 $p=2$ 是欧氏，$p=1$ 是曼哈顿。

### 2.2 为什么必须标准化

面积（几十～上百）vs 距地铁（几公里）：不缩放时，**大数值特征垄断距离**。  
阶段测试强调：KNN 靠距离，量纲差很大必须先 **StandardScaler**。

---

## 三、关键参数

### 3.1 $K$（邻居个数）

| $K$ | 现象 | 风险 |
| --- | --- | --- |
| 太小（如 1） | 完全跟最近点走 | 噪声敏感，易**过拟合** |
| 太大 | 被全局多数/均值淹没 | 边界过平滑，易**欠拟合** |

选 $K$：交叉验证；分类常用奇数减轻平票。

### 3.2 `weights`

| 取值 | 含义 |
| --- | --- |
| `uniform` | 邻居票权相同 |
| `distance` | 更近的邻居权更大 |

`distance` 更灵活，也对噪声更敏感。

### 3.3 预测规则

- **分类**：多数表决；可输出邻居比例当粗糙概率  
- **回归**：邻居 $y$ 的平均或加权平均  

---

## 四、业务场景与局限

### 4.1 适合

- 局部结构明显、解释要「像哪几个样本」  
- 推荐系统里常做 **召回层**（先找相似候选），不是最终精细排序  

### 4.2 不适合 / 变差时

- 特征很多（高维距离失效）  
- 噪声大、类别编码乱  
- 样本量极大（预测要扫很多点，慢）  

### 4.3 优缺点

**优点**：直观、非参数、好实现。  
**缺点**：预测贵、吃距离与尺度、高维差、占存储。

---

## 五、综合代码（逐行注释）

```python
import numpy as np  # 数值计算
import pandas as pd  # 表格
from sklearn.model_selection import train_test_split, cross_val_score  # 划分与 CV
from sklearn.preprocessing import StandardScaler  # 标准化
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor, NearestNeighbors  # 三类用法
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error  # 指标
from sklearn.datasets import load_iris  # 鸢尾花

# ========== 1) 分类：会员购买（小样本演示口径） ==========
member = pd.DataFrame({  # 会员数据
    "age": [22, 25, 47, 52, 46, 56, 23, 27, 48, 50],  # 年龄
    "active_hours": [35, 40, 10, 12, 15, 8, 30, 38, 14, 9],  # 活跃时长
    "buy_member": [1, 1, 0, 0, 0, 0, 1, 1, 0, 0],  # 是否购买
})
X_m = member[["age", "active_hours"]]  # 特征
y_m = member["buy_member"]  # 标签
Xm_tr, Xm_te, ym_tr, ym_te = train_test_split(  # 划分
    X_m, y_m, test_size=0.3, random_state=42, stratify=y_m  # 分层防测试集全一类
)
sc_m = StandardScaler()  # 标准化器
Xm_tr_s = sc_m.fit_transform(Xm_tr)  # 训练拟合+转换
Xm_te_s = sc_m.transform(Xm_te)  # 测试只转换
clf = KNeighborsClassifier(n_neighbors=3)  # K=3 分类
clf.fit(Xm_tr_s, ym_tr)  # 「训练」=记住样本
print("会员测试准确率:", accuracy_score(ym_te, clf.predict(Xm_te_s)))  # 小样本可能虚高
print("新用户预测:", clf.predict(sc_m.transform([[24, 33]])))  # 年轻高活跃常判购买

# ========== 2) 回归：房价 ==========
house = pd.DataFrame({  # 房价
    "area": [60, 70, 80, 85, 90, 100, 110, 120],  # 面积
    "distance_to_subway": [1.2, 0.8, 1.5, 0.5, 0.4, 2.0, 1.0, 0.3],  # 距地铁
    "price": [180, 210, 230, 280, 290, 250, 310, 340],  # 价格
})
Xh_tr, Xh_te, yh_tr, yh_te = train_test_split(  # 划分
    house[["area", "distance_to_subway"]], house["price"], test_size=0.25, random_state=42
)
sc_h = StandardScaler()  # 缩放
Xh_tr_s = sc_h.fit_transform(Xh_tr)  # 训练缩放
Xh_te_s = sc_h.transform(Xh_te)  # 测试缩放
reg = KNeighborsRegressor(n_neighbors=3, weights="distance")  # 加权回归
reg.fit(Xh_tr_s, yh_tr)  # 存数据
yp = reg.predict(Xh_te_s)  # 预测
print("房价 MAE:", round(mean_absolute_error(yh_te, yp), 4))  # MAE
print("房价 MSE:", round(mean_squared_error(yh_te, yp), 4))  # MSE
print("新房预测:", round(reg.predict(sc_h.transform([[88, 0.6]]))[0], 2))  # 88㎡近地铁

# ========== 3) 扫 K：Iris ==========
iris = load_iris()  # 载入
Xi_tr, Xi_te, yi_tr, yi_te = train_test_split(  # 划分
    iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target
)
sc_i = StandardScaler()  # 缩放
Xi_tr_s = sc_i.fit_transform(Xi_tr)  # 训练
Xi_te_s = sc_i.transform(Xi_te)  # 测试
for k in range(1, 11):  # 扫 K
    knn = KNeighborsClassifier(n_neighbors=k)  # 建模型
    knn.fit(Xi_tr_s, yi_tr)  # 拟合
    acc = accuracy_score(yi_te, knn.predict(Xi_te_s))  # 测试准确率
    print(f"K={k}: Acc={acc:.4f}")  # 打印；K=1 常高但不稳

# ========== 4) 相似商品召回 ==========
goods = pd.DataFrame({  # 商品特征
    "price": [4999, 5999, 8999, 4599, 5299, 7999],  # 价格
    "weight": [1.2, 1.4, 2.3, 1.1, 1.25, 2.1],  # 重量
    "battery": [15, 12, 8, 16, 14, 9],  # 续航
    "score": [80, 82, 95, 78, 81, 93],  # 性能分
}, index=["A轻薄", "C办公", "G游戏", "H便携", "E长续航", "F旗舰"])  # 名称
sc_g = StandardScaler()  # 缩放
Gs = sc_g.fit_transform(goods)  # 标准化特征
nn = NearestNeighbors(n_neighbors=4, metric="euclidean")  # 找近邻（含自己）
nn.fit(Gs)  # 建索引
dist, idx = nn.kneighbors(Gs[[0]])  # 查 A 款
print("与 A 最相似（去掉自身）:")  # 标题
for d, i in zip(dist[0][1:], idx[0][1:]):  # 跳过自己
    print(goods.index[i], "距离", round(d, 4))  # 打印候选
```

---

## 六、易错点、自测、练习

1. 不标准化。  
2. $K=1$ 当最优不验证。  
3. 高维硬上 KNN。  
4. 把召回层效果当成最终排序效果。  
5. 分类划分不做 `stratify`。  

自测：$K$ 太小/太大？懒惰学习？Minkowski $p=1/2$？推荐常作哪一层？  
答案：过拟合/欠拟合；训练存数据预测再算；曼哈顿/欧氏；召回层。

---

## 七、一句话收束

> KNN 用距离找邻居做投票或平均：直觉强，但必须标准化、认真选 $K$，并警惕高维与预测成本。

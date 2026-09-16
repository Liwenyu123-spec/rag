"""
2026-09-15 模拟实验考试卷 — 完整填空答案版
共 10 题，可分段运行（每题独立）。
"""

# =============================================================================
# 第一题 机房日志状态映射 + 温度分段离散化
# ① str.lower()  ② map(status_dict)  ③ pd.cut(..., bins=bins, labels=labels)
# =============================================================================
import pandas as pd

data = {
    "设备编码": ["S101", "S102", "S103", "S104", "S105"],
    "状态码": ["RUN", "STOP", "run", "FAULT", "stop"],
    "CPU温度": [33.5, 78.2, 41.6, 92.4, 62.1],
}
df = pd.DataFrame(data)
print("=== 第一题：原始机房日志 ===")
print(df)

status_dict = {"run": "运行", "stop": "停机", "fault": "故障"}

df["小写状态"] = df["状态码"].str.lower()
df["设备状态"] = df["小写状态"].map(status_dict)

bins = [25, 45, 65, 85, 100]
labels = ["低温", "正常", "高温", "超温"]
df["温度风险"] = pd.cut(df["CPU温度"], bins=bins, labels=labels)

print("\n=== 标准化、离散化后完整数据 ===")
print(df)


# =============================================================================
# 第二题 水质传感器异常值边界截断
# ① 越界布尔索引  ② clip(lower=..., upper=...)
# =============================================================================
import numpy as np

data = {
    "监测点": ["W001", "W002", "W003", "W004", "W005"],
    "PH值": [7.1, 12.8, 6.5, -2.3, 7.4],
    "浊度": [12, 45, 120, 22, -5],
}
df = pd.DataFrame(data)
print("\n=== 第二题：原始水质检测数据 ===")
print(df)

min_limit = 0
max_limit = 50

abnormal_data = df[
    ((df[["PH值", "浊度"]] < min_limit) | (df[["PH值", "浊度"]] > max_limit)).any(axis=1)
]
print("\n=== 检测到异常数据行 ===")
print(abnormal_data)

num_columns = df.select_dtypes(include="number").columns
df[num_columns] = df[num_columns].clip(lower=min_limit, upper=max_limit)

print("\n=== 异常值截断修正完成数据 ===")
print(df)


# =============================================================================
# 第三题 企业利润多元线性回归
# ① X[:, 1:]  ② LinearRegression()  ③ model.fit(X_train, y_train)
# =============================================================================
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

data = {
    "研发投入": [145200, 138900, 160100, 132500, 151000],
    "管理费用": [120500, 142300, 112800, 98600, 105300],
    "城市": ["杭州", "广州", "杭州", "成都", "广州"],
    "利润": [178500, 183200, 190100, 162400, 171300],
}
dataset = pd.DataFrame(data)
print("\n=== 第三题：企业经营原始数据集 ===")
print(dataset)

X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

le = LabelEncoder()
X[:, 2] = le.fit_transform(X[:, 2])

ct = ColumnTransformer([("onehot", OneHotEncoder(), [2])], remainder="passthrough")
X = np.asarray(ct.fit_transform(X))

# 删除独热编码后的第一列，规避虚拟变量陷阱
X = X[:, 1:]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

print("多元线性回归模型训练完成！")
print(f"系数：{model.coef_}，截距：{model.intercept_:.2f}")


# =============================================================================
# 第四题 客服文本意图朴素贝叶斯分类
# ① CountVectorizer()  ② MultinomialNB()  ③ bayes_clf.fit(...)
# =============================================================================
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

data = {
    "text": [
        "物流配送太慢要求投诉",
        "商品质量差要退款投诉",
        "怎么修改订单收货时间",
        "如何申请价保服务",
        "建议增加线上客服人工通道",
        "希望优化商品搜索筛选功能",
    ],
    "label": ["投诉", "投诉", "咨询", "咨询", "建议", "建议"],
}
df = pd.DataFrame(data)
print("\n=== 第四题：客服反馈原始文本数据 ===")
print(df)

vec = CountVectorizer()
X_text = vec.fit_transform(df["text"])

bayes_clf = MultinomialNB()
bayes_clf.fit(X_text, df["label"])

print("客服意图分类朴素贝叶斯模型训练完毕！")
print("词表大小：", len(vec.get_feature_names_out()))


# =============================================================================
# 第五题 员工薪资单变量线性回归 + R² 评估
# ① train_test_split(...)  ② lr.fit(...)  ③ r2_score(y_test, y_pred)
# =============================================================================
from sklearn.metrics import r2_score

data = {
    "工作年限": [
        1.0, 1.5, 2.1, 2.4, 3.2, 3.5, 4.0, 4.6, 5.2, 6.1, 6.7, 7.3, 8.0, 9.2, 10.0
    ],
    "薪资": [
        38000, 42000, 45000, 48500, 53000, 56200, 61000, 65800, 72000, 81000,
        86000, 92500, 98000, 110000, 118000,
    ],
}
dataset = pd.DataFrame(data)
print("\n=== 第五题：员工薪资数据集前5行 ===")
print(dataset.head())

X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

lr = LinearRegression()
lr.fit(X_train, y_train)

y_pred = lr.predict(X_test)
r2_result = r2_score(y_test, y_pred)

print(f"回归斜率：{lr.coef_[0]:.2f}")
print(f"截距：{lr.intercept_:.2f}")
print(f"模型R2评估分数：{r2_result:.4f}")


# =============================================================================
# 第六题 学生数学成绩分布可视化
# ① plt.subplots(1, 2)  ② plot(kind='hist', ...)  ③ plot.box
# =============================================================================
import matplotlib.pyplot as plt

data = {
    "Math_Score": [
        85, 72, 90, 68, 78, 82, 95, 65, 76, 88,
        70, 81, 92, 74, 69, 83, 77, 86, 91, 79,
        60, 75, 87, 93, 71, 80, 84, 73, 67, 89,
        94, 66, 78, 82, 76, 85, 70, 88, 96, 55,
        79, 81, 77, 83, 90, 72, 86, 98, 64, 100,
    ]
}
df = pd.DataFrame(data)
score_data = df["Math_Score"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
fig.suptitle("学生数学期末成绩分布分析图")

# 试卷填空答案：score_data.plot(kind='hist', ax=ax1, bins=10, kde=True)
# 新版 pandas 的 hist 不再支持 kde=True，这里拆成直方图 + 密度曲线，效果等价
score_data.plot.hist(ax=ax1, bins=10, density=True, alpha=0.7)
score_data.plot.kde(ax=ax1)
ax1.set_xlabel("考试分数")
ax1.set_ylabel("人数")
ax1.set_title("成绩直方图(含密度曲线)")

score_data.plot.box(ax=ax2)
ax2.set_xlabel("数学成绩")
ax2.set_title("成绩箱线图（识别异常值）")
plt.tight_layout()
# 有图形界面时取消下一行注释即可弹窗；默认保存到文件便于无界面运行
fig.savefig("915_score_dist.png", dpi=120)
print("\n=== 第六题：成绩分布图已保存为 915_score_dist.png ===")
plt.close(fig)


# =============================================================================
# 第七题 车间温度噪声填充（-999 为异常）
# ① replace  ② bfill()  ③ fillna
# =============================================================================
temp_data = [24.3, 24.5, -999, 24.8, 25.1, -999, 25.0, -999, 24.7, 24.9]
df = pd.DataFrame(temp_data, columns=["Temperature"])
print("\n=== 第七题：原始温度数据 ===")
print(df)

df_clean = df.replace(-999, np.nan)
df_clean["温度_bfill填充"] = df_clean["Temperature"].bfill()

med_val = df_clean["Temperature"].median()
df_clean["温度_中位数填充"] = df_clean["Temperature"].fillna(med_val)

print("\n噪声填充后完整数据：")
print(df_clean)


# =============================================================================
# 第八题 电商用户行为特征标准化
# ① sklearn.preprocessing import StandardScaler
# ② StandardScaler()  ③ transformed
# =============================================================================
from sklearn.preprocessing import StandardScaler

data = {
    "月消费金额": [260, 580, 390, 920, 1500, 720],
    "月浏览时长(分钟)": [110, 320, 240, 510, 760, 430],
    "月下单次数": [2, 6, 3, 8, 12, 5],
}
df = pd.DataFrame(data)
feature_cols = df.columns

std_scaler = StandardScaler()
transformed = std_scaler.fit_transform(df[feature_cols])
df_standard = pd.DataFrame(transformed, columns=feature_cols)

print("\n=== 第八题：用户原始行为数据 ===")
print(df)
print("\n标准化后用户特征：")
print(df_standard)


# =============================================================================
# 第九题 商品销量数据基础统计分析
# ① describe()  ② median()  ③ corr(...)
# =============================================================================
np.random.seed(123)
data = {
    "Daily_Sales": np.random.normal(120, 25, 100),
    "Page_Views": np.random.uniform(500, 2000, 100),
}
df = pd.DataFrame(data)

print("\n=== 第九题：数据整体描述统计 ===")
print(df.describe())

sales_median = df["Daily_Sales"].median()
print(f"\n商品日销量中位数：{sales_median:.2f}")

corr_val = df["Daily_Sales"].corr(df["Page_Views"])
print(f"\n销量与页面浏览量相关系数：{corr_val:.4f}")


# =============================================================================
# 第十题 外卖配送时长多特征线性回归
# ① train_test_split(...)  ② lr.fit(...)  ③ r2_score(y_test, y_pred)
# =============================================================================
np.random.seed(42)
n_samples = 120
distance = np.random.uniform(1, 8, n_samples)
prep_time = np.random.uniform(0, 25, n_samples)
noise = np.random.normal(0, 2, n_samples)
delivery_time = 3 + 2.2 * distance + 0.7 * prep_time + noise

df = pd.DataFrame(
    {
        "Distance": distance,
        "PrepTime": prep_time,
        "DeliveryTime": delivery_time,
    }
)

X = df[["Distance", "PrepTime"]].values
y = df["DeliveryTime"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

lr = LinearRegression()
lr.fit(X_train, y_train)

y_pred = lr.predict(X_test)
r2 = r2_score(y_test, y_pred)
print("\n=== 第十题：外卖配送回归 ===")
print(f"模型系数：{lr.coef_}, 截距：{lr.intercept_:.2f}")
print(f"测试集R2得分：{r2:.4f}")

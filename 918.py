# import faiss
# import numpy as np

# # 第一步：创建示例数据
# dimension = 128  # 向量维度
# num_vectors = 10000  # 向量数量

# # 生成随机向量（实际应用中来自文本嵌入模型）
# # 生成一个num_vectors行dimension列的随机数矩阵
# # vectors 是一个 10000×128 的矩阵：
# #
# # [
# #   [0.12, 0.45, 0.89, ..., 0.34],  ← 向量0 (128维)
# #   [0.67, 0.23, 0.91, ..., 0.56],  ← 向量1 (128维)
# #   [0.34, 0.78, 0.12, ..., 0.89],  ← 向量2 (128维)
# #   ...
# #   [0.56, 0.12, 0.67, ..., 0.23]   ← 向量9999 (128维)
# # ]
# vectors = np.random.random((num_vectors, dimension)).astype('float32')

# # 第二步：创建索引对象
# index = faiss.IndexFlatL2(dimension)  # 使用L2距离（欧氏距离）的精确索引

# # 第三步：将向量添加到索引对象里
# # 注意事项：
# # 向量一旦添加，不能单独修改或删除（FAISS的限制）
# # 如果需要更新，通常需要重建索引
# index.add(vectors)
# print(f"索引已添加 {index.ntotal} 个向量")

# # 第四步：执行查询
# # 1）、生成查询向量
# query = np.random.random((1, dimension)).astype('float32')
# print(f"查询向量：{query}")

# # 2）、执行查询
# k = 5  # 返回最相似的5个结果
# distances, indices = index.search(query, k)

# print(f"\n查询结果：")
# for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
#    print(f"第{i+1}相似向量：索引{idx}，距离{distance:.4f}")

import faiss
import numpy as np

dimension = 128 # 向量的维度
nlist = 100  # 将空间划分为100个聚类中心

# 第一步：创建量化器（底层的精确索引）
quantizer = faiss.IndexFlatL2(dimension)

# 第二步：创建IVF索引对象
index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# 第三步：训练索引（必需！），才能使用索引进行搜索。
print("训练索引中...")
# 1、生成10000个128维的向量的矩阵（就是库中的数据）
vectors = np.random.random((10000, dimension)).astype('float32')
index.train(vectors)  # 使用k-means找到聚类中心
print("训练完成")

# 第四步：添加数据到索引中。
index.add(vectors)

# 第五步：设置搜索参数
index.nprobe = 10  # 搜索最近的10个聚类中心

# 第六步：查询
# 1）、生成需要查询的向量（相当于用户搜索的内容的向量）
query = np.random.random((1, dimension)).astype('float32')
# 2）、执行查询
distances, indices = index.search(query, k=5)
# 3）、输出距离最近的5个向量的索引，也就是语义相似的5个向量的索引。
print(f"查询结果：{indices}")
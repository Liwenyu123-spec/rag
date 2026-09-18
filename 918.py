# # import faiss
# # import numpy as np

# # # 第一步：创建示例数据
# # dimension = 128  # 向量维度
# # num_vectors = 10000  # 向量数量

# # # 生成随机向量（实际应用中来自文本嵌入模型）
# # # 生成一个num_vectors行dimension列的随机数矩阵
# # # vectors 是一个 10000×128 的矩阵：
# # #
# # # [
# # #   [0.12, 0.45, 0.89, ..., 0.34],  ← 向量0 (128维)
# # #   [0.67, 0.23, 0.91, ..., 0.56],  ← 向量1 (128维)
# # #   [0.34, 0.78, 0.12, ..., 0.89],  ← 向量2 (128维)
# # #   ...
# # #   [0.56, 0.12, 0.67, ..., 0.23]   ← 向量9999 (128维)
# # # ]
# # vectors = np.random.random((num_vectors, dimension)).astype('float32')

# # # 第二步：创建索引对象
# # index = faiss.IndexFlatL2(dimension)  # 使用L2距离（欧氏距离）的精确索引

# # # 第三步：将向量添加到索引对象里
# # # 注意事项：
# # # 向量一旦添加，不能单独修改或删除（FAISS的限制）
# # # 如果需要更新，通常需要重建索引
# # index.add(vectors)
# # print(f"索引已添加 {index.ntotal} 个向量")

# # # 第四步：执行查询
# # # 1）、生成查询向量
# # query = np.random.random((1, dimension)).astype('float32')
# # print(f"查询向量：{query}")

# # # 2）、执行查询
# # k = 5  # 返回最相似的5个结果
# # distances, indices = index.search(query, k)

# # print(f"\n查询结果：")
# # for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
# #    print(f"第{i+1}相似向量：索引{idx}，距离{distance:.4f}")

# import faiss
# import numpy as np

# dimension = 128 # 向量的维度
# nlist = 100  # 将空间划分为100个聚类中心

# # 第一步：创建量化器（底层的精确索引）
# quantizer = faiss.IndexFlatL2(dimension)

# # 第二步：创建IVF索引对象
# index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

# # 第三步：训练索引（必需！），才能使用索引进行搜索。
# print("训练索引中...")
# # 1、生成10000个128维的向量的矩阵（就是库中的数据）
# vectors = np.random.random((10000, dimension)).astype('float32')
# index.train(vectors)  # 使用k-means找到聚类中心
# print("训练完成")

# # 第四步：添加数据到索引中。
# index.add(vectors)

# # 第五步：设置搜索参数
# index.nprobe = 10  # 搜索最近的10个聚类中心

# # 第六步：查询
# # 1）、生成需要查询的向量（相当于用户搜索的内容的向量）
# query = np.random.random((1, dimension)).astype('float32')
# # 2）、执行查询
# distances, indices = index.search(query, k=5)
# # 3）、输出距离最近的5个向量的索引，也就是语义相似的5个向量的索引。
# print(f"查询结果：{indices}")



import chromadb

client = chromadb.PersistentClient(path="./chroma_data")

# 方式1：添加文档（自动生成向量）
# collection = client.get_or_create_collection("kaoqin")
# collection.add(
#     documents=[
#         "正常工作时间：周一至周五：9:00 - 18:00。可以弹性处理一个小时。如：9:30-18:30，午休时间：12:00-13:30",
#         "年假：员工入职满一年后可以享受带薪年假 3 天，每增加一年工龄增加 1 天，最多不超过 10 天。年假需提前一周申请，经部门主管批准后安排。年假为带薪假",
#         "婚假：结婚证登记日期在试用期内的员工，可在试用期通过后申请婚假，婚假天数以员工合同签署地法律法规为准。需提供结婚证复印件。建议一次性休完。婚假为带薪假"
#     ],
#     metadatas=[
#             {"category": "工作时间"},
#             {"category": "年假" },
#             {"category": "婚假"}
#         ],
#     ids=["doc1", "doc2", "doc3"]
# )

# 方式2：直接添加向量（跳过嵌入生成）
import numpy as np
# 随机产生3个384维向量。
collection = client.get_collection("ruzhi")

vectors = np.random.random((3, 384)).astype('float32')  # 384维向量
collection.add(
    embeddings=vectors,
    documents=["文档1", "文档2", "文档3"],
    metadatas=[{"type": "direct"}, {"type": "direct"}, {"type": "direct"}],
    ids=["vec1", "vec2", "vec3"]
)

#
# 方式3：批量添加（提高性能）
# collection = client.get_or_create_collection("jihe")
# batch_size = 10
# documents = [f"文档{i}" for i in range(100)]   
# metadatas = [{"index": i} for i in range(100)]
# ids = [f"doc{i}" for i in range(100)]
#
# # 分批添加
# for i in range(0, len(documents), batch_size):
#     collection.add(
#         documents=documents[i:i+batch_size],
#         metadatas=metadatas[i:i+batch_size],
#         ids=ids[i:i+batch_size]
#     )
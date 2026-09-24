"""检索前优化（Pre-retrieval）：清洗 → 重写 / HyDE。

对应讲义第 08 章常用落地路径：
方法1 查询清洗 + 方法3 查询重写；可选方法5 HyDE（假想文档检索）。
假想文档只用于检索，绝不作为事实引用。
"""  # 模块说明：检索进入向量库之前的查询侧优化

from __future__ import annotations  # 允许注解里写尚未定义的类型

import re  # 用正则去掉口语填充词、标点噪音
from typing import Any  # LLM 参数用 Any，避免强绑具体实现类

# 口语/无信息填充词（方法1 Step1）
_FILLER_PATTERNS = [  # 要剔除的口语填充正则列表
    r"嗯+",  # 连续「嗯」
    r"啊+",  # 连续「啊」
    r"那个",  # 口语停顿词
    r"这个",  # 口语停顿词
    r"帮我看看",  # 客套话
    r"帮我查一下",  # 客套话
    r"请问一下",  # 客套话
    r"请问",  # 客套话
    r"麻烦",  # 客套话
    r"一下",  # 弱化语气词
    r"咋样",  # 口语
]

# 简单术语表：口语 → 制度用语（方法1 Step3）
_TERM_MAP = {  # 把用户口语映射成知识库更可能出现的正式词
    "电脑": "笔记本电脑",  # 口语「电脑」→ 正式「笔记本电脑」
    "年假": "带薪年假",  # 对齐制度用语
    "咋扣钱": "如何扣款",  # 口语问法 → 检索友好问法
    "扣钱": "扣款",  # 统一扣款术语
    "请假咋": "请假如何",  # 口语 → 规范表达
}


REWRITE_PROMPT = """你是检索改写助手。把用户问题改写成更适合知识库向量检索的中文问句。
要求：
1. 只输出改写后的一句问句，不要解释、不要引号
2. 补全实体与关键词，保留原意
3. 可加入同义术语，不要编造不存在的产品或制度名
4. 去掉口语废话

用户问题：{query}
改写："""  # 查询重写提示词模板，{query} 会被填入清洗后的问题

HYDE_PROMPT = """请写一段可能回答下列问题的「制度/说明文」片段，用于向量检索。
要求：
1. 用说明文/制度口吻，不要对话、不要第一人称闲聊
2. 100～200 字，包含可能出现在正式文档里的关键词
3. 只输出假想文档正文，不要标题、不要解释
4. 内容可以是合理推测，仅用于检索，不是最终答案

问题：{query}
假想文档："""  # HyDE 提示词：生成假想答案文档，仅用于检索


def clean_query(text: str) -> str:  # 方法1：查询文本清洗
    """方法1：查询文本清洗 → clean_query。"""  # 函数文档字符串
    query = (text or "").strip()  # 空值保护并去掉首尾空白
    if not query:  # 清洗后若为空
        return ""  # 直接返回空串

    # Step1 去口语填充
    for pattern in _FILLER_PATTERNS:  # 逐个填充词模式处理
        query = re.sub(pattern, " ", query, flags=re.IGNORECASE)  # 匹配到的填充词替换成空格

    # Step2 去标点噪音、多余空白、表情式重复符号
    query = re.sub(r"[?？!！。.~～…]+", " ", query)  # 连续标点换成空格
    query = re.sub(r"\s+", " ", query).strip()  # 多空白压成单空格并再 trim

    # Step3 术语标准化
    for src, dst in _TERM_MAP.items():  # 遍历口语→正式用语映射
        if src in query:  # 原句里出现口语词才替换
            query = query.replace(src, dst)  # 换成制度/文档侧用语

    return query or (text or "").strip()  # 若洗空了则退回原始去空白文本


def _llm_text(llm: Any, prompt: str) -> str:  # 调用 LLM 并抽出纯文本
    """统一从 LlamaIndex LLM 取纯文本。"""  # 兼容 complete() 返回对象
    response = llm.complete(prompt)  # 同步补全一次
    text = str(response).strip()  # 转字符串并去首尾空白
    # 去掉模型偶发的引号包裹
    if (text.startswith("「") and text.endswith("」")) or (  # 中文直角引号包裹
        len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'`"  # 成对英文/反引号包裹
    ):
        text = text[1:-1].strip()  # 剥掉首尾引号再 trim
    return text  # 返回干净文本


def rewrite_query(llm: Any, query: str) -> str:  # 方法3：查询重写
    """方法3：查询重写 Query Rewriting → rewritten_query。"""  # 函数说明
    rewritten = _llm_text(llm, REWRITE_PROMPT.format(query=query))  # 填模板并让 LLM 改写
    return rewritten or query  # 模型空输出时回退原 query


def hyde_document(llm: Any, query: str) -> str:  # 方法5：HyDE 假想文档
    """方法5：HyDE 生成假想答案文档 → hypo_doc（仅用于检索）。"""  # 函数说明
    hypo = _llm_text(llm, HYDE_PROMPT.format(query=query))  # 让 LLM 写假想说明文
    return hypo or query  # 失败则退回原 query，避免检索无输入


def prepare_retrieval_queries(  # 按策略组装检索用查询列表
    question: str,  # 用户原问题
    strategy: str,  # none / clean / rewrite / hyde
    llm: Any | None = None,  # 需要重写/HyDE 时传入全局 LLM
) -> dict:  # 返回中间产物字典，供 API 与前端展示
    """按策略产出检索用查询列表与中间产物。

    strategy:
      - none: 原问题直接检索
      - clean: 仅清洗
      - rewrite: 清洗 + 重写（原句+改写句双路，防改歪）
      - hyde: 清洗 + HyDE（原句+假想文档双路，对应 include_original=True）
    """  # 策略说明文档
    strategy = (strategy or "rewrite").strip().lower()  # 默认 rewrite，并统一小写
    original = (question or "").strip()  # 规范化原问题
    cleaned = clean_query(original)  # 先做方法1清洗

    meta: dict = {  # 中间产物：方便作业演示与调试
        "strategy": strategy,  # 实际采用的策略名
        "original_query": original,  # 用户原问题
        "clean_query": cleaned,  # 清洗后的问题
        "rewritten_query": None,  # 重写结果（rewrite 时填）
        "hyde_doc": None,  # 假想文档（hyde 时填）
        "retrieval_queries": [],  # 真正拿去 retriever 的查询列表
    }

    if strategy == "none":  # 不做任何优化
        meta["retrieval_queries"] = [original]  # 只用原问题检索
        return meta  # 提前返回

    if strategy == "clean":  # 只清洗
        meta["retrieval_queries"] = [cleaned]  # 只用清洗句检索
        return meta  # 提前返回

    if llm is None:  # 需要 LLM 的策略却没传入模型
        meta["retrieval_queries"] = [cleaned or original]  # 退化为清洗（或原句）单路
        return meta  # 避免空引用崩溃

    if strategy == "hyde":  # HyDE：假想文档检索
        hypo = hyde_document(llm, cleaned or original)  # 生成假想说明文
        meta["hyde_doc"] = hypo  # 记录假想文档（不当最终答案引用）
        # 假想文档 + 原清洗句两路（讲义强烈建议保留原查询）
        queries = []  # 去重后的双路查询
        for q in (cleaned, hypo):  # 先清洗句，再假想文档
            if q and q not in queries:  # 非空且未重复
                queries.append(q)  # 追加一路
        meta["retrieval_queries"] = queries  # 写入检索列表
        return meta  # HyDE 分支结束

    # 默认 rewrite
    rewritten = rewrite_query(llm, cleaned or original)  # 清洗后再重写
    meta["rewritten_query"] = rewritten  # 记录改写句
    queries = []  # 双路：清洗句 + 改写句，防改歪漏检
    for q in (cleaned, rewritten):  # 遍历两路
        if q and q not in queries:  # 去重追加
            queries.append(q)
    meta["retrieval_queries"] = queries  # 写入检索列表
    return meta  # 返回完整中间产物

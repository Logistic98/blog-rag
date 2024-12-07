# -*- coding: utf-8 -*-


# 用于判断文档片段与用户问题相关性的Prompt
RELEVANT_PROMPT_TEMPLATE = """你是一个智能助手，负责判断给定的文档片段是否对回答用户的问题有帮助。
文档片段：
{chunk_text}

问题：
{query}

请回答：这段文档对回答问题有帮助吗？请仅回答“是”或“否”。"""

# 用于生成答案的Prompt
ANSWER_INSTRUCTION_TEMPLATE = """你是一个智能助手，你需要从知识库中选择你需要的信息来回答用户问题，请阅读知识库，利用相关信息回答用户问题。

## 当前日期：{current_date}

## 知识库：\n\n{kb_text}"""

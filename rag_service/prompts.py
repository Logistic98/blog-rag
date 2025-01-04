# -*- coding: utf-8 -*-

# 用于扩展原始问题的Prompt
def build_rewrite_prompt(original_question: str, question_rewrite_num: int) -> str:
    """
    根据 question_rewrite_num 动态生成 JSON 数组格式，用于请求 LLM 扩展问题。
    """
    prompt = f"""
请阅读用户的问题，然后重新组织并扩展成 {question_rewrite_num} 个不同问法。
用户问题：{original_question}

请按如下 **严格格式** 返回结果。请不要包含任何解释或注释，也不要使用 Markdown 代码块，请直接返回 JSON：

[
"""
    for i in range(question_rewrite_num):
        prompt += f"""  {{
    "type": "rewrite",
    "question": "重写问题{i+1}"
  }}"""
        if i < question_rewrite_num - 1:
            prompt += ",\n"
        else:
            prompt += "\n"
    prompt += "]"""
    return prompt


# 用于判断文档片段与用户问题相关性的Prompt
RELEVANT_PROMPT_TEMPLATE = """你是一个智能助手，负责判断给定的文档片段是否对回答用户的问题有帮助。
文档片段：
{chunk_text}

问题：
{query}

请回答：这段文档对回答问题有帮助吗？请仅回答“是”或“否”。"""

# 用于生成答案的Prompt
ANSWER_PROMPT_TEMPLATE = """你是一个智能助手，你需要从知识库中选择相关信息来回答用户的问题。在回答时，请特别注意以下几点：

1. **图片链接处理**：如果回答中涉及Markdown格式的图片链接，请务必保留这些图片链接，并确保它们出现在相关内容的上下文中。
   - 图片通常是对于上文的文本内容的补充，每个图片链接应紧跟在其相关文本之后，且确保该图片的作用和上下文内容相匹配。
   - 图片名称能够提供提示作用，请根据上下文判断它是展示示意图、结果图还是其他类型的图片，并按照需要调整图片的位置。

2. **知识库内容使用**：请尽量从知识库中提取出准确和相关的信息，构建回答时避免遗漏关键细节。保证回答简洁、准确且具有针对性。

3. **输出格式**：请确保你的回答格式清晰，图像和文本在语义上是连贯的。确保不丢失任何相关内容，并尽可能详细地保留配图描述。

## 当前日期：{current_date}

## 知识库：\n\n{kb_text}"""




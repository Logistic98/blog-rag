# -*- coding: utf-8 -*-


from prompts import RELEVANT_PROMPT_TEMPLATE


async def judge_relevant(llm, model, strategy, threshold, query, chunk, history=[]):
    if strategy == "llm":
        prompt = RELEVANT_PROMPT_TEMPLATE.format(chunk_text=chunk['text'][:500], query=query)
        response = await llm.chat_no_stream(
            model, [*history, {"role": "user", "content": prompt}],
            temperature=0, extra_body={"guided_choice": ["否", "是"]}
        )
        return response["choices"][0]["message"]["content"].strip() == "是"
    elif strategy == "thres":
        return chunk.get("score", float('inf')) <= threshold, chunk
    return False

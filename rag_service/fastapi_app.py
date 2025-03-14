# -*- coding: utf-8 -*-

import json
import asyncio
import time
import uuid
import re

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
from config import Config
from knowledge_base import KnowledgeBase
from llm import LLM
from models import ChatCompletionRequest
from validators import chunk_judge_relevant, chat_judge_relevant
from logging_setup import logger
from prompts import build_rewrite_prompt, ANSWER_PROMPT_TEMPLATE, CONTEXT_REWRITE_PROMPT_TEMPLATE


def generate_stream_response(
    request_id, model, step, message, references=None, content=None, finish_reason=None
):
    """
    用于生成流式返回的 JSON 数据。
    """
    return {
        "id": request_id,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {
                    "role": None,
                    "content": content,
                    "reference": references if references else [],
                    "step": step,
                    "message": message
                },
                "finish_reason": finish_reason
            }
        ]
    }


def deduplicate_chunks(chunks):
    """
    去重切片，切片的text相同则视为是一个，只保留每组中得分最高的切片。
    """
    retrieved_chunks_map = {}

    for chunk in chunks:
        chunk_copy = chunk.copy()
        score_value = chunk_copy.pop('score', None)

        chunk_key = frozenset(chunk_copy.items())

        if chunk_key not in retrieved_chunks_map:
            retrieved_chunks_map[chunk_key] = {
                'score': score_value,
                **chunk_copy
            }
        else:
            existing_score = retrieved_chunks_map[chunk_key]['score']
            if score_value > existing_score:
                retrieved_chunks_map[chunk_key] = {
                    'score': score_value,
                    **chunk_copy
                }

    deduplicated_chunks = []
    for chunk_key, chunk_data in retrieved_chunks_map.items():
        restored_chunk = {
            'score': chunk_data['score'],
            **dict(chunk_key)
        }
        deduplicated_chunks.append(restored_chunk)

    return deduplicated_chunks


async def rewrite_contextual_references(llm: LLM, model: str, original_question: str, history_messages: list) -> str:
    """
    使用 LLM 对用户原始问题中的上下文指代进行重写，输出调整后的完整明确问题。
    若失败，直接返回原问题。
    """
    history_str = "\n".join([f"{msg['role']}：{msg['content']}" for msg in history_messages])
    context_rewrite_prompt = CONTEXT_REWRITE_PROMPT_TEMPLATE.format(
        history=history_str,
        question=original_question
    )
    try:
        response = await llm.chat_no_stream(
            model,
            [
                {"role": "system", "content": "你是一个上下文问题重写助手。"},
                {"role": "user", "content": context_rewrite_prompt}
            ],
            temperature=0.3
        )
        adjusted_question = response["choices"][0]["message"]["content"].strip()
        return adjusted_question if adjusted_question else original_question
    except Exception as e:
        logger.warning(f"上下文指代重写失败: {e}")
        return original_question


async def rewrite_question(llm: LLM, model: str, original_question: str, question_rewrite_num: int) -> list:
    """
    使用 LLM 将用户的原始问题进行扩展，返回新的问题列表。
    根据 question_rewrite_num 生成对应数量的重写问法。
    如果 JSON 解析失败或内容不符合预期，会进行3次重试，全部重试失败则只返回原问题。
    """
    rewrite_prompt = build_rewrite_prompt(original_question, question_rewrite_num)
    max_retry = 3

    for attempt in range(1, max_retry + 1):
        logger.info(f"第 {attempt} 次尝试重写扩展...")
        rewrite_response = await llm.chat_no_stream(
            model,
            [
                {"role": "system", "content": "你是一个问题扩展助手，可以帮我对原问题进行扩展。"},
                {"role": "user", "content": rewrite_prompt}
            ],
            temperature=0.7
        )

        content = rewrite_response["choices"][0]["message"]["content"]
        logger.info(f"重写扩展结果（尝试 {attempt}）: {content}")
        content_without_backticks = re.sub(r"```(json)?(.*?)```", r"\2", content, flags=re.DOTALL).strip()

        try:
            expansions = json.loads(content_without_backticks)
            if not isinstance(expansions, list):
                raise ValueError("解析结果不是列表。")

            questions = [item["question"] for item in expansions if "question" in item]
            if len(questions) < question_rewrite_num:
                raise ValueError("重写问题数不足。")

            return questions

        except Exception as e:
            logger.warning(f"重写扩展解析失败 (第 {attempt} 次): {e}")
            if attempt < max_retry:
                await asyncio.sleep(0.02)
            else:
                logger.warning("已达最大重试次数，放弃重写扩展。")

    return [original_question]


async def decorate_answer(
    request_id, llm, model, chunks, messages, temperature=None, extra_body=None, stop=None, stream=False
):
    """
    将从知识库中检索到的chunks放入最终回答指令，生成答案。
    """
    kb_text = "\n\n".join(chunk["text"] for chunk in chunks)
    instruction = ANSWER_PROMPT_TEMPLATE.format(
        current_date=time.strftime("%Y年%m月%d日", time.localtime()),
        kb_text=kb_text
    )

    if stream:
        async for response in llm.chat_stream(
            model,
            [{"role": "system", "content": instruction}, *messages],
            temperature,
            extra_body,
            stop
        ):
            for choice in response.get('choices', []):
                content = choice['delta'].get('content', None)
                if content not in [None, ""]:
                    choice['delta'].update({"step": 4, "message": "正在总结...", "reference": []})
                    response['id'] = request_id
                    yield response
    else:
        response = await llm.chat_no_stream(
            model,
            [{"role": "system", "content": instruction}, *messages],
            temperature,
            extra_body,
            stop
        )
        response['id'] = request_id
        yield response


async def handle_streaming_response(data, llm, kb):
    """
    主要处理流程:
    1. 对原问题进行重写扩展
    2. 判断是否需检索知识库
    3. 检索相关的知识库数据
    4. 大模型总结并返回答案
    """
    request_id = str(uuid.uuid4())
    model = kb.config.LLM_MODEL
    cot_model = kb.config.LLM_COT_MODEL
    messages = [{"role": msg.role, "content": msg.content} for msg in data.messages]
    last_message_content = messages[-1]["content"]
    logger.info(f'用户输入的传参: {json.dumps(data.dict(), ensure_ascii=False)}')
    full_response = ''
    references = []
    needs_retrieve_chunk = True

    # Step 1: 对原问题进行重写扩展
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 1, '调整问题上下文指代信息...'), ensure_ascii=False)}\n\n"
    adjusted_question = await rewrite_contextual_references(llm, model, last_message_content, messages[:-1])
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 1, f'根据上下文重写后的问题为：{adjusted_question}'), ensure_ascii=False)}\n\n"
    logger.info(f"上下文重写后的问题: {adjusted_question}")
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 1, '对问题进行重写扩展...'), ensure_ascii=False)}\n\n"
    if kb.config.QUESTION_REWRITE_ENABLED:
        await asyncio.sleep(0)
        expanded_questions = await rewrite_question(
            llm, model, adjusted_question, kb.config.QUESTION_REWRITE_NUM
        )
        expanded_questions.append(adjusted_question)
    else:
        expanded_questions = [adjusted_question]
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 1, f'重写扩展为{len(expanded_questions)}个问题'), ensure_ascii=False)}\n\n"
    logger.info(f"重写扩展后的问题：{expanded_questions}")

    # Step 2: 判断是否需检索知识库
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 2, '判断是否需检索知识库...'), ensure_ascii=False)}\n\n"
    if kb.config.QUESTION_RETRIEVE_ENABLED:
        judgments = []
        for eq in expanded_questions:
            is_relevant = await chat_judge_relevant(llm, model, eq, messages[:-1])
            judgments.append(is_relevant)
        relevant_count = sum(1 for j in judgments if j)
        needs_retrieve_chunk = relevant_count >= len(expanded_questions) / 2
        if not needs_retrieve_chunk:
            logger.info(f'不需要检索知识库，大模型直接生成...')
            yield f"data: {json.dumps(generate_stream_response(request_id, model, 2, '不需要检索知识库，大模型直接生成...'), ensure_ascii=False)}\n\n"

    # Step 3: 检索相关的知识库数据
    if (kb.config.QUESTION_RETRIEVE_ENABLED and needs_retrieve_chunk) or not kb.config.QUESTION_RETRIEVE_ENABLED:
        yield f"data: {json.dumps(generate_stream_response(request_id, model, 3, '检索文档切片中...'), ensure_ascii=False)}\n\n"
        await asyncio.sleep(0)
        search_tasks = [kb.retrieve(q, kb.config.RETRIEVE_TOPK, file_types=['chunk']) for q in expanded_questions]
        all_results = await asyncio.gather(*search_tasks)
        retrieved_chunks = []
        for (chunks, refs) in all_results:
            retrieved_chunks.extend(chunks)
        retrieved_chunks = deduplicate_chunks(retrieved_chunks)
        logger.info(f'检索出的文档切片: {retrieved_chunks}')
        logger.info(f'检索出的相关文档数量: {len(retrieved_chunks)}')
        yield f"data: {json.dumps(generate_stream_response(request_id, model, 3, '数据相关性分析中...'), ensure_ascii=False)}\n\n"
        tasks = [
            chunk_judge_relevant(llm, model, kb.config.STRATEGY, kb.config.THRESHOLD, last_message_content, chunk, messages[:-1])
            for chunk in retrieved_chunks
        ]
        relevancy_results = await asyncio.gather(*tasks)
        hit_chunks = [chunk for chunk, is_rel in zip(retrieved_chunks, relevancy_results) if is_rel][:kb.config.RETRIEVE_TOPK]
        doc_names = [chunk['doc_name'] for chunk in hit_chunks if chunk['doc_name']]
        references = list(dict.fromkeys(doc_names))
        logger.info(f'相关性判断后的文档切片: {hit_chunks}')
        logger.info(f'相关性判断后的相关文档数量: {len(hit_chunks)}')
        yield f"data: {json.dumps(generate_stream_response(request_id, model, 3, f'存在{len(hit_chunks)}条相关数据'), ensure_ascii=False)}\n\n"
    else:
        yield f"data: {json.dumps(generate_stream_response(request_id, model, 3, '跳过知识库文档检索...'), ensure_ascii=False)}\n\n"

    # Step 4: 总结最终答案
    yield f"data: {json.dumps(generate_stream_response(request_id, cot_model, 4, '正在总结答案...'), ensure_ascii=False)}\n\n"
    if needs_retrieve_chunk and 'hit_chunks' in locals() and hit_chunks:
        async for response in decorate_answer(request_id, llm, cot_model, hit_chunks, messages,
                                              data.temperature, data.extra_body, data.stop, stream=True):
            for choice in response.get('choices', []):
                content = choice['delta'].get('content', None)
                if content not in [None, ""]:
                    full_response += content
            for choice in response.get('choices', []):
                choice['delta']['reference'] = []
            yield f"data: {json.dumps(response, ensure_ascii=False)}\n\n"

        final_chunk = generate_stream_response(request_id, cot_model, 4, '回答完成', references)
        logger.info(f'流式输出最终响应: {full_response}')
        yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"

    else:
        async for response in llm.chat_stream(
            model,
            [{"role": "system", "content": last_message_content}, *messages],
            data.temperature,
            data.extra_body,
            data.stop
        ):
            for choice in response.get('choices', []):
                content = choice['delta'].get('content', None)
                if content not in [None, ""]:
                    full_response += content
                    wrapped_resp = generate_stream_response(
                        request_id=request_id,
                        model=model,
                        step=4,
                        message="正在总结...",
                        references=references,
                        content=content
                    )
                    choice['delta'].update(wrapped_resp['choices'][0]['delta'])

            response['id'] = request_id
            response['model'] = model
            yield f"data: {json.dumps(response, ensure_ascii=False)}\n\n"

        logger.info(f'流式输出最终响应: {full_response}')

    yield "data: [DONE]\n\n"


async def handle_non_streaming_response(data, llm, kb):
    """
    主要处理流程:
    1. 对原问题进行重写扩展
    2. 判断是否需检索知识库
    3. 检索相关的知识库数据
    4. 大模型总结并返回答案
    """
    request_id = str(uuid.uuid4())
    model = kb.config.LLM_MODEL
    cot_model = kb.config.LLM_COT_MODEL
    messages = [{"role": msg.role, "content": msg.content} for msg in data.messages]
    last_message_content = messages[-1]["content"]
    logger.info(f'用户输入的传参: {json.dumps(data.dict(), ensure_ascii=False)}')
    references = []
    needs_retrieve_chunk = True

    # Step 1: 对原问题进行重写扩展
    adjusted_question = await rewrite_contextual_references(llm, model, last_message_content, messages[:-1])
    logger.info(f"上下文重写后的问题: {adjusted_question}")
    if kb.config.QUESTION_REWRITE_ENABLED:
        expanded_questions = await rewrite_question(
            llm, model, last_message_content, kb.config.QUESTION_REWRITE_NUM
        )
        expanded_questions.append(adjusted_question)
    else:
        expanded_questions = [adjusted_question]
    logger.info(f"重写扩展后的问题：{expanded_questions}")

    # Step 2: 判断是否需检索知识库
    if kb.config.QUESTION_RETRIEVE_ENABLED:
        judgments = []
        for eq in expanded_questions:
            is_relevant = await chat_judge_relevant(llm, model, eq, messages[:-1])
            judgments.append(is_relevant)
        relevant_count = sum(1 for j in judgments if j)
        needs_retrieve_chunk = relevant_count >= len(expanded_questions) / 2
        if not needs_retrieve_chunk:
            logger.info(f'不需要检索知识库，大模型直接生成...')

    # Step 3: 检索相关的知识库数据
    if (kb.config.QUESTION_RETRIEVE_ENABLED and needs_retrieve_chunk) or not kb.config.QUESTION_RETRIEVE_ENABLED:
        logger.info("检索文档切片中...")
        search_tasks = [kb.retrieve(q, kb.config.RETRIEVE_TOPK, file_types=['chunk']) for q in expanded_questions]
        all_results = await asyncio.gather(*search_tasks)
        retrieved_chunks = []
        for (chunks, refs) in all_results:
            retrieved_chunks.extend(chunks)
        retrieved_chunks = deduplicate_chunks(retrieved_chunks)
        logger.info(f'检索出的文档切片: {retrieved_chunks}')
        logger.info(f'检索出的相关文档数量: {len(retrieved_chunks)}')
        tasks = [
            chunk_judge_relevant(
                llm, model, kb.config.STRATEGY, kb.config.THRESHOLD,
                last_message_content, chunk, messages[:-1]
            )
            for chunk in retrieved_chunks
        ]
        relevancy_results = await asyncio.gather(*tasks)
        hit_chunks = [chunk for chunk, is_rel in zip(retrieved_chunks, relevancy_results) if is_rel][:kb.config.RETRIEVE_TOPK]
        doc_names = [chunk['doc_name'] for chunk in hit_chunks if chunk['doc_name']]
        references = list(dict.fromkeys(doc_names))
        logger.info(f'相关性判断后的文档切片: {hit_chunks}')
        logger.info(f'相关性判断后的相关文档数量: {len(hit_chunks)}')
    else:
        hit_chunks = []
        logger.info("不需要检索知识库，大模型直接生成...")

    # Step 4: 返回最终回答
    if needs_retrieve_chunk and hit_chunks:
        async for response in decorate_answer(
            request_id, llm, cot_model, hit_chunks, messages,
            data.temperature, data.extra_body, data.stop, stream=False
        ):
            response['choices'][0]['message']['reference'] = references
            logger.info(f'非流式输出最终响应: {response["choices"][0]["message"]["content"]}')
            return response
    else:
        response = await llm.chat_no_stream(cot_model, messages, data.temperature, data.extra_body, data.stop)
        response['choices'][0]['message']['reference'] = []
        response["id"] = request_id
        logger.info(f'非流式最终响应: {response["choices"][0]["message"]["content"]}')
        return response


def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"]
    )
    config = Config()
    kb = KnowledgeBase(config)
    llm = LLM(config.LLM_BASE_URL, config.LLM_API_KEY)

    async def verify_api_key(config: Config, authorization: Optional[str] = Header(None)):
        if not config.API_KEYS:
            logger.info("API Key 校验已跳过，因为配置中未定义任何合法 API Key。")
            return
        if not authorization:
            logger.warning("缺少 Authorization 头部")
            raise HTTPException(status_code=401, detail="Missing Authorization Header")
        if not authorization.startswith("Bearer "):
            logger.warning(f"Authorization 格式错误: {authorization}")
            raise HTTPException(status_code=402, detail="Invalid Authorization Header")
        token = authorization.split("Bearer ")[1]
        if token not in config.API_KEYS:
            logger.warning(f"非法的 API Key 尝试: {token}")
            raise HTTPException(status_code=403, detail="Invalid API Key")

    @app.post("/v1/chat/completions")
    async def completions(data: ChatCompletionRequest, authorization: Optional[str] = Header(None)):
        await verify_api_key(config, authorization)
        if data.stream:
            return StreamingResponse(
                handle_streaming_response(data, llm, kb),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
            )
        else:
            response = await handle_non_streaming_response(data, llm, kb)
            return response

    return app


app = create_app()

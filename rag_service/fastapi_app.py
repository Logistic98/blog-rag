# -*- coding: utf-8 -*-

import json
import asyncio
import time
import uuid

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
from config import Config
from knowledge_base import KnowledgeBase
from llm import LLM
from models import ChatCompletionRequest
from validators import judge_relevant
from logging_setup import logger
from prompts import ANSWER_INSTRUCTION_TEMPLATE


def generate_stream_response(request_id, model, step, message, references=None, content=None, finish_reason=None):
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


async def decorate_answer(request_id, llm, model, chunks, messages, temperature=None, extra_body=None, stop=None, stream=False):
    kb_text = "\n\n".join(chunk["text"] for chunk in chunks)
    instruction = ANSWER_INSTRUCTION_TEMPLATE.format(
        current_date=time.strftime("%Y年%m月%d日", time.localtime()),
        kb_text=kb_text
    )

    if stream:
        async for response in llm.chat_stream(model, [{"role": "system", "content": instruction}, *messages],
                                              temperature, extra_body, stop):
            for choice in response.get('choices', []):
                content = choice['delta'].get('content', None)
                if content not in [None, ""]:
                    choice['delta'].update({"step": 3, "message": "正在总结...", "reference": []})
                    response['id'] = request_id
                    yield response
    else:
        response = await llm.chat_no_stream(model, [{"role": "system", "content": instruction}, *messages], temperature,
                                            extra_body, stop)
        response['id'] = request_id
        yield response


async def handle_streaming_response(data, llm, kb):
    request_id = str(uuid.uuid4())
    model = kb.config.LLM_MODEL
    messages = [{"role": msg.role, "content": msg.content} for msg in data.messages]
    last_message_content = messages[-1]["content"]
    logger.info(f'用户输入的传参: {json.dumps(data.dict(), ensure_ascii=False)}')
    full_response = ''

    # Step 1: 检索相关文档
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 1, '数据检索中...'), ensure_ascii=False)}\n\n"
    await asyncio.sleep(0)
    relevants, _ = await kb.retrieve(last_message_content, kb.config.RETRIEVE_TOPK)
    logger.info(f'检索出的相关文档数量: {len(relevants)}')
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 1, f'检索到{len(relevants)}条数据'), ensure_ascii=False)}\n\n"

    # Step 2: 判断相关性
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 2, '相关性分析中...'), ensure_ascii=False)}\n\n"
    tasks = [judge_relevant(llm, model, kb.config.STRATEGY, kb.config.THRESHOLD, last_message_content, chunk, messages[:-1])
             for chunk in relevants]
    relevancy_results = await asyncio.gather(*tasks)

    hit_chunks = [chunk for chunk, is_relevant in zip(relevants, relevancy_results) if is_relevant][
                 :kb.config.RETRIEVE_TOPK]
    doc_names = [chunk['doc_name'] for chunk in hit_chunks if chunk['doc_name']]
    references = list(dict.fromkeys(doc_names))
    yield f"data: {json.dumps(generate_stream_response(request_id, model, 2, f'存在{len(hit_chunks)}条相关数据'), ensure_ascii=False)}\n\n"
    logger.info(f'使用的参考文档: {references}')

    # Step 3: 总结最终答案
    async for response in decorate_answer(request_id, llm, model, hit_chunks, messages, data.temperature,
                                          data.extra_body, data.stop, stream=True):
        for choice in response.get('choices', []):
            content = choice['delta'].get('content', None)
            if content not in [None, ""]:
                full_response += content if content is not None else ''
        for choice in response.get('choices', []):
            choice['delta']['reference'] = []
        yield f"data: {json.dumps(response, ensure_ascii=False)}\n\n"

    final_chunk = generate_stream_response(request_id, model, 3, '回答完成', references)
    final_chunk['choices'][0]['finish_reason'] = "stop"
    logger.info(f'流式输出最终响应: {full_response}')
    yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"

    yield "data: [DONE]\n\n"


async def handle_non_streaming_response(data, llm, kb):
    request_id = str(uuid.uuid4())
    model = kb.config.LLM_MODEL
    messages = [{"role": msg.role, "content": msg.content} for msg in data.messages]
    last_message_content = messages[-1]["content"]
    logger.info(f'用户输入的传参: {json.dumps(data.dict(), ensure_ascii=False)}')

    # Step 1: 检索相关文档
    relevants, _ = await kb.retrieve(last_message_content, kb.config.RETRIEVE_TOPK)
    logger.info(f'检索出的相关文档数量: {len(relevants)}')

    # Step 2: 判断相关性
    tasks = [judge_relevant(llm, model, kb.config.STRATEGY, kb.config.THRESHOLD, last_message_content, chunk, messages[:-1])
             for chunk in relevants]
    relevancy_results = await asyncio.gather(*tasks)
    hit_chunks = [chunk for chunk, is_relevant in zip(relevants, relevancy_results) if is_relevant][
                 :kb.config.RETRIEVE_TOPK]
    doc_names = [chunk['doc_name'] for chunk in hit_chunks if chunk['doc_name']]
    references = list(dict.fromkeys(doc_names))
    logger.info(f'使用的参考文档: {references}')

    # Step 3: 返回最终回答
    if hit_chunks:
        async for response in decorate_answer(request_id, llm, model, hit_chunks, messages, data.temperature,
                                              data.extra_body, data.stop, stream=False):
            response['choices'][0]['message']['reference'] = references
            logger.info(f'非流式最终响应: {response["choices"][0]["message"]["content"]}')
            return response
    else:
        response = await llm.chat_no_stream(model, messages, data.temperature, data.extra_body, data.stop)
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
            raise HTTPException(status_code=401, detail="Invalid Authorization Header")
        token = authorization.split("Bearer ")[1]
        if token not in config.API_KEYS:
            logger.warning(f"非法的 API Key 尝试: {token}")
            raise HTTPException(status_code=401, detail="Invalid API Key")

    @app.post("/v1/chat/completions")
    async def completions(data: ChatCompletionRequest, authorization: Optional[str] = Header(None)):
        await verify_api_key(config, authorization)
        if data.stream:
            return StreamingResponse(handle_streaming_response(data, llm, kb), media_type="text/event-stream",
                                     headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
        else:
            response = await handle_non_streaming_response(data, llm, kb)
            return response

    return app


app = create_app()
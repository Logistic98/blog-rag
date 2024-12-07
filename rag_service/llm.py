# -*- coding: utf-8 -*-

import asyncio
from openai import OpenAI


class LLM:
    def __init__(self, base_url: str, api_key: str):
        self.model = OpenAI(base_url=base_url, api_key=api_key)

    async def chat_stream(self, model, messages, temperature=None, extra_body=None, stop=None):
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()

        def run_in_executor():
            completion_result = self.model.chat.completions.create(
                model=model, messages=messages, temperature=temperature,
                extra_body=extra_body, stop=stop, stream=True
            )
            for shard in completion_result:
                result = self._standard_stream_response(shard)
                loop.call_soon_threadsafe(queue.put_nowait, result)
            loop.call_soon_threadsafe(queue.put_nowait, None)

        executor = None
        loop.run_in_executor(executor, run_in_executor)

        while True:
            result = await queue.get()
            if result is None:
                break
            yield result

    async def chat_no_stream(self, model, messages, temperature=None, extra_body=None, stop=None):
        completion_result = await asyncio.to_thread(
            self.model.chat.completions.create,
            model=model, messages=messages, temperature=temperature,
            extra_body=extra_body, stop=stop, stream=False
        )
        return self._standard_no_stream_response(completion_result)

    def _standard_stream_response(self, resp):
        return {
            "id": resp.id, "model": resp.model,
            "choices": [
                {
                    "index": choice.index,
                    "delta": {
                        "role": getattr(choice.delta, "role", None),
                        "content": getattr(choice.delta, "content", None),
                    },
                    "finish_reason": choice.finish_reason,
                } for choice in resp.choices
            ],
        }

    def _standard_no_stream_response(self, resp):
        return {
            "id": resp.id, "object": resp.object,
            "created": resp.created, "model": resp.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                        "tool_calls": choice.message.tool_calls,
                    },
                    "finish_reason": choice.finish_reason,
                } for choice in resp.choices
            ],
            "usage": {
                "prompt_tokens": resp.usage.prompt_tokens,
                "completion_tokens": resp.usage.completion_tokens,
                "total_tokens": resp.usage.total_tokens,
            },
        }

# -*- coding: utf-8 -*-

from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Any


class FunctionAvailable(BaseModel):
    type: str = "function"
    function: Optional[FunctionDefinition] = None


class ChatCompletionMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatCompletionMessage]
    extra_body: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False

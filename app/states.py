from typing import TypedDict

from langgraph.graph import MessagesState


class Request(TypedDict):
    method: str
    path: str
    query_params: dict
    body: dict


class MainState(MessagesState):
    request: Request
    user_command: str
    plan: str
    denied: bool
    denied_reason: str


class MainOutputState(TypedDict):
    status_code: int
    body: dict
    headers: dict

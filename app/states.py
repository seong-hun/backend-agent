from typing import TypedDict
from langgraph.graph import MessagesState


class MainState(MessagesState):
    method: str
    path: str
    query_params: dict
    body: dict
    command: str
    logic: str


class MainOutputState(TypedDict):
    status_code: int
    body: dict
    headers: dict

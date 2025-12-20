from typing import Literal

from langgraph.graph import MessagesState

from app.schemas import Response


class MainState(MessagesState):
    stage: Literal["start", "tool_call", "end"]
    response: Response

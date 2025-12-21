from typing import Literal
from langgraph.graph import MessagesState


class SqlState(MessagesState):
    tables: str
    schema: str
    stage: Literal["start", "tool_call", "end"]

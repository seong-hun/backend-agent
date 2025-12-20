from langgraph.graph import MessagesState


class SqlState(MessagesState):
    user_command: str
    tables: str
    schema: str

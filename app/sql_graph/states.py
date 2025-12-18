from langgraph.graph import MessagesState


class SqlState(MessagesState):
    user_query: str
    tables: str
    schema: str

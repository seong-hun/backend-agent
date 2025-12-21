from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.sql_graph import nodes, states, tools


def should_continue(state: states.SqlState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "check_query"


def build_sql_graph():
    builder = StateGraph(states.SqlState)

    builder.add_node(nodes.handler)
    builder.add_node("tools", ToolNode([tools.run_query_tool]))

    builder.add_edge(START, "handler")
    builder.add_conditional_edges("handler", tools_condition, ["tools", END])
    builder.add_edge("tools", "handler")

    sql_graph = builder.compile()
    return sql_graph


sql_graph = build_sql_graph()

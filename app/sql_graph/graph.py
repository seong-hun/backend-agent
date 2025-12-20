from langgraph.graph import END, START, StateGraph

from app.sql_graph import nodes, states


def should_continue(state: states.SqlState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "check_query"


def build_sql_graph():
    builder = StateGraph(states.SqlState)
    builder.add_node(nodes.generate_query)
    builder.add_node(nodes.check_query)
    builder.add_node(nodes.run_query_tool_node)

    builder.add_edge(START, "generate_query")
    builder.add_conditional_edges(
        "generate_query", should_continue, ["check_query", END]
    )
    builder.add_edge("check_query", "run_query_tool_node")
    builder.add_edge("run_query_tool_node", "generate_query")

    sql_graph = builder.compile()
    return sql_graph


sql_graph = build_sql_graph()

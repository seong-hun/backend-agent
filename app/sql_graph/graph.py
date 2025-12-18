from langgraph.graph import END, START, StateGraph

from app.sql_graph import nodes, states


def build_sql_graph():
    def should_continue(state: states.SqlState):
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:
            return END
        else:
            return "check_query"

    builder = StateGraph(states.SqlState)
    builder.add_node(nodes.list_tables)
    builder.add_node(nodes.call_get_schema)
    builder.add_node("get_schema", nodes.get_schema_node)
    builder.add_node(nodes.generate_query)
    builder.add_node(nodes.check_query)
    builder.add_node("run_query", nodes.run_query_node)

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges(
        "generate_query",
        should_continue,
    )
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")

    sql_graph = builder.compile()
    return sql_graph


sql_graph = build_sql_graph()

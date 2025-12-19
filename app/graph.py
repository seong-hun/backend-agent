from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app import nodes, tools
from app.states import MainOutputState, MainState


def build_main_graph():
    builder = StateGraph(MainState, output_schema=MainOutputState)

    # Add nodes
    builder.add_node(nodes.request_parser)
    builder.add_node(nodes.logic_generator)
    builder.add_node(nodes.handler)
    builder.add_node(
        "tools",
        ToolNode([tools.call_sql_graph, *tools.jwt_tools, *tools.password_tools]),
    )
    builder.add_node(nodes.responser)

    # Add edges
    builder.add_edge(START, "request_parser")
    builder.add_edge("request_parser", "logic_generator")
    builder.add_edge("logic_generator", "handler")
    builder.add_conditional_edges(
        "handler",
        tools_condition,
        {
            "tools": "tools",
            END: "responser",
        },
    )
    builder.add_edge("tools", "handler")

    graph = builder.compile()

    module_dir = Path(__file__).parents[1] / "assets"
    module_dir.mkdir(parents=True, exist_ok=True)
    graph.get_graph().draw_png(
        output_file_path=str(module_dir / "graph.png"),
    )
    return graph


main_graph = build_main_graph()

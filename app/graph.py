import logging
from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app import nodes, tools
from app.states import MainState

logger = logging.getLogger(__name__)


def build_main_graph():
    builder = StateGraph(MainState)

    # Add nodes
    builder.add_node(nodes.handler)
    builder.add_node(nodes.responder)
    builder.add_node("tools", ToolNode(tools.handler_tools))

    # Add edges
    builder.add_edge(START, "handler")
    builder.add_conditional_edges(
        "handler", tools_condition, {"tools": "tools", "__end__": "responder"}
    )
    builder.add_edge("tools", "handler")
    builder.add_edge("responder", END)

    graph = builder.compile()

    module_dir = Path(__file__).parents[1] / "assets"
    module_dir.mkdir(parents=True, exist_ok=True)
    graph.get_graph().draw_png(
        output_file_path=str(module_dir / "graph.png"),
    )
    return graph


main_graph = build_main_graph()

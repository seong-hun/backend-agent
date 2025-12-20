import logging
from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app import nodes, tools
from app.states import MainOutputState, MainState

logger = logging.getLogger(__name__)


def should_continue(state: MainState):
    if state["denied"]:
        logger.info("The requeset is denied.")
        logger.info(f"  Reason: {state['denied_reason']}")
        return "responser"

    if not state["plan"]:
        logger.info("Plan was not generated. Try again.")
        return "response"

    return "handler"


def build_main_graph():
    builder = StateGraph(MainState, output_schema=MainOutputState)

    # Add nodes
    builder.add_node(nodes.translator)
    builder.add_node(nodes.planner)
    builder.add_node(nodes.handler)
    builder.add_node("tools", ToolNode(tools.handler_tools))
    builder.add_node(nodes.responser)

    # Add edges
    builder.add_edge(START, "translator")
    builder.add_edge("translator", "planner")
    builder.add_conditional_edges("planner", should_continue, ["handler", "responser"])
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

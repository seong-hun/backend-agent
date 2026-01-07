import logging

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from app.common.databases import db_manager
from app.common.models import get_model
from app.common.utils import response_to_text
from app.obs.event_bus import event_bus
from app.sql_graph import prompts, tools
from app.sql_graph.states import SqlState

logger = logging.getLogger(__name__)


async def handler(state: SqlState):
    prefix = "[Node sql_graph - handler]"

    stage = state.get("stage")
    if stage is None:
        stage = "start"
        input_content = state["messages"][-1].content
        logger.info(f"{prefix} Input: {input_content}")

        await event_bus.publish(
            {
                "type": "node",
                "graph": "sql_graph",
                "name": "handler",
                "status": "start",
            },
        )

    tables = ", ".join(db_manager.list_tables())
    schema = db_manager.get_schema_text()

    if stage == "tool_call":
        tool_response = state["messages"][-1].content
        logger.info(f"{prefix} Tool Result: {tool_response}")

    system_message = SystemMessage(
        content=prompts.generate_query_prompt.format(
            dialect=db_manager.get_dialect(),
            top_k=5,
            tables=tables,
            schema=schema,
        )
    )
    model = get_model("large")
    model_prefix = f"[{model.name}]"

    response = model.bind_tools([tools.run_query_tool]).invoke(
        [system_message] + state["messages"]
    )

    if response.tool_calls:
        stage = "tool_call"
        logger.info(
            f"{prefix} {model_prefix} Calling a tool: {response_to_text(response)}"
        )

        for tool_call in response.tool_calls:
            await event_bus.publish(
                {
                    "type": "tool",
                    "graph": "sql_graph",
                    "name": tool_call["name"],
                    "status": "start",
                    "content": tool_call["args"],
                },
            )

    elif response.content:
        stage = "respond"
        logger.info(f"{prefix} {model_prefix} Final response: {response.content}")

    return {"stage": stage, "messages": [response]}


run_query_tool_node = ToolNode([tools.run_query_tool], name="run_query_tool_node")

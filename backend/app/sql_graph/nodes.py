import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from app.common.databases import db_manager
from app.common.models import get_model
from app.common.utils import record, response_to_text
from app.sql_graph import prompts, tools
from app.sql_graph.states import SqlState

logger = logging.getLogger(__name__)


@record
def handler(state: SqlState):
    prefix = "[Node sql_graph - handler]"

    stage = state.get("stage")
    if stage is None:
        stage = "start"
        logger.info(f"{prefix} Input: {state['messages'][-1].content}")

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
    elif response.content:
        stage = "respond"
        logger.info(f"{prefix} {model_prefix} Final response: {response.content}")

    return {"stage": stage, "messages": [response]}


run_query_tool_node = ToolNode([tools.run_query_tool], name="run_query_tool_node")

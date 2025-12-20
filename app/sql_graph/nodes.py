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
def generate_query(state: SqlState):
    prefix = "[Node sql_graph - generate_query]"
    logger.info(f"{prefix} Start")

    user_command = state["user_command"]

    tables = ", ".join(db_manager.list_tables())
    schema = db_manager.get_schema_text()

    if state["messages"] and state["messages"][-1].type == "tool":
        tool_response = state["messages"][-1].content
        logger.info(f"{prefix} Tool Result: {tool_response}")
    else:
        tool_response = ""

    system_message = SystemMessage(
        content=prompts.generate_query_prompt.format(
            dialect=db_manager.get_dialect(),
            top_k=5,
            tables=tables,
            schema=schema,
            user_command=user_command,
            tool_response=tool_response,
        )
    )
    response = (
        get_model("medium")
        .bind_tools([tools.run_query_tool])
        .invoke([system_message] + state["messages"])
    )

    logger.info(f"{prefix} Reponse: {response_to_text(response)}")
    return {"messages": [response]}


@record
def check_query(state: SqlState):
    prefix = "[Node sql_graph - check_query]"
    logger.info(f"{prefix} Start")

    system_message = SystemMessage(
        content=prompts.check_query_prompt.format(dialect=db_manager.get_dialect())
    )
    tool_call = state["messages"][-1].tool_calls[0]
    user_message = HumanMessage(content=tool_call["args"]["query"])
    llm_with_tools = get_model("medium").bind_tools(
        [tools.run_query_tool], tool_choice="any"
    )
    response = llm_with_tools.invoke([system_message, user_message])
    response.id = state["messages"][-1].id

    logger.info(
        f"{prefix} Revised Query: ({response.messages[-1].tool_calls[0]['args']['query']})"
    )

    return {"messages": [response]}


run_query_tool_node = ToolNode([tools.run_query_tool], name="run_query_tool_node")

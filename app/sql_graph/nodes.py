from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from app.common.models import get_model
from app.common.utils import record, response_to_text
from app.common.databases import db
from app.sql_graph import tools, prompts
from app.sql_graph.states import SqlState

import logging

logger = logging.getLogger(__name__)


@record
def list_tables(state: SqlState):
    prefix = "[Node sql_graph - list_tables]"
    logger.info(f"{prefix} Start")

    tool_call = {
        "name": "sql_db_list_tables",
        "args": {},
        "id": "abc123",
        "type": "tool_call",
    }
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])
    tool_message = tools.list_tables_tool.invoke(tool_call)
    response = AIMessage(f"Available tables: {tool_message.content}")

    logger.info(f"{prefix} {response.content}")
    return {"messages": [tool_call_message, tool_message, response]}


@record
def call_get_schema(state: SqlState):
    prefix = "[Node sql_graph - call_get_schema]"
    logger.info(f"{prefix} Start")

    llm_with_tools = get_model("medium").bind_tools(
        [tools.get_schema_tool], tool_choice="any"
    )
    response = llm_with_tools.invoke(state["messages"])

    logger.info(f"{prefix} Response: {response_to_text(response)}")
    return {"messages": [response]}


@record
def generate_query(state: SqlState):
    prefix = "[Node sql_graph - generate_query]"
    logger.info(f"{prefix} Start")

    system_message = SystemMessage(
        content=prompts.generate_query_prompt.format(
            dialect=db.dialect,
            top_k=5,
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
        content=prompts.check_query_prompt.format(dialect=db.dialect)
    )
    tool_call = state["messages"][-1].tool_calls[0]
    user_message = HumanMessage(content=tool_call["args"]["query"])
    llm_with_tools = get_model("medium").bind_tools(
        [tools.run_query_tool], tool_choice="any"
    )
    response = llm_with_tools.invoke([system_message, user_message])
    response.id = state["messages"][-1].id

    logger.info(f"{prefix} Check query: {user_message}")
    logger.info(f"{prefix} Result: {response_to_text(response)}")

    return {"messages": [response]}


list_tables_node = ToolNode([tools.list_tables_tool], name="list_tables")
get_schema_node = ToolNode([tools.get_schema_tool], name="get_schema")
run_query_node = ToolNode([tools.run_query_tool], name="run_query")

generate_query_tools_node = ToolNode(
    [tools.list_tables_tool, tools.get_schema_tool, tools.run_query_tool],
    name="generate_query_tools",
)

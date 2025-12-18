import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from app.common.databases import db
from app.common.models import get_model
from app.common.utils import record, response_to_text
from app.sql_graph import prompts, tools
from app.sql_graph.states import SqlState

logger = logging.getLogger(__name__)


@record
def get_db_info(state: SqlState):
    prefix = "[Node sql_graph - list_tables]"
    logger.info(f"{prefix} Start")

    tables = tools.list_tables_tool.invoke({})
    logger.info(f"{prefix} Avaliable tables: {tables}")
    if not tables:
        schema = ""

    schema = tools.get_schema_tool.invoke(tables)
    logger.info(f"{prefix} schema: {schema}")

    user_query = state["user_query"]
    messages = [HumanMessage(content=user_query)]
    logger.info(f"{prefix} user_query: {user_query}")
    return {"tables": tables, "schema": schema, "messages": messages}


@record
def generate_query(state: SqlState):
    prefix = "[Node sql_graph - generate_query]"
    logger.info(f"{prefix} Start")

    user_query = state["user_query"]
    tables = state["tables"]
    schema = state["schema"]

    last_message = state["messages"][-1]
    if last_message.type == "tool":
        tool_response = last_message.content
        logger.info(f"{prefix} Tool Result: {tool_response}")
    else:
        tool_response = ""

    system_message = SystemMessage(
        content=prompts.generate_query_prompt.format(
            dialect=db.dialect,
            top_k=5,
            tables=tables,
            schema=schema,
            user_query=user_query,
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


@record
def response(state: SqlState):
    pass


list_tables_tool_node = ToolNode([tools.list_tables_tool], name="list_tables_tool_node")
get_schema_tool_node = ToolNode([tools.get_schema_tool], name="get_schema_tool_node")
run_query_tool_node = ToolNode([tools.run_query_tool], name="run_query_tool_node")

generate_query_tools_node = ToolNode(
    [tools.list_tables_tool, tools.get_schema_tool, tools.run_query_tool],
    name="generate_query_tools",
)

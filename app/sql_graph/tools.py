from langchain_community.agent_toolkits import SQLDatabaseToolkit

from app.common.databases import db_manager
from app.common.models import get_model


class SqlToolkit:
    def __init__(self):
        toolkit = SQLDatabaseToolkit(db=db_manager.get_db(), llm=get_model("medium"))
        self.tools = toolkit.get_tools()

    def find_tool(self, name):
        return next(tool for tool in self.tools if tool.name == name)


sql_toolkit = SqlToolkit()

list_tables_tool = sql_toolkit.find_tool("sql_db_list_tables")
get_schema_tool = sql_toolkit.find_tool("sql_db_schema")
run_query_tool = sql_toolkit.find_tool("sql_db_query")

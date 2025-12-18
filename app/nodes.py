from langchain_core.messages import HumanMessage, SystemMessage

from app import prompts, tools
from app.common.models import get_model
from app.common.utils import get_recorder, record
from app.states import MainOutputState, MainState

recorder = get_recorder()


@record
def request_parser(state: MainState):
    system_message = SystemMessage(content=prompts.parse_request_prompt)
    human_message = HumanMessage(
        content=f"""
            method: {state["method"]},
            path: {state["path"]},
            query_params: {state["query_params"]},
            body: {state["body"]},
        """
    )
    response = get_model("medium").invoke([system_message, human_message])
    return {"command": response.content}


@record
def logic_generator(state: MainState):
    system_message = SystemMessage(content=prompts.logic_generator_prompt)
    human_message = HumanMessage(content=state["command"])
    response = get_model("medium").invoke([system_message, human_message])
    return {"logic": response.content}


@record
def handler(state: MainState):
    logic = state["logic"]
    system_message = SystemMessage(content=prompts.handler_prompt.format(logic=logic))
    model = get_model("medium").bind_tools([tools.call_sql_graph, *tools.jwt_tools])
    response = model.invoke([system_message, *state["messages"]])

    return {"messages": [response]}


@record
def responser(state: MainState):
    logic = state["logic"]
    system_message = SystemMessage(content=prompts.responser_prompt.format(logic=logic))
    model = get_model("medium").with_structured_output(MainOutputState)
    response = model.invoke([system_message, *state["messages"]])
    return {"response": response}

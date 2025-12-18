from langchain_core.messages import HumanMessage, SystemMessage

from app import prompts, tools
from app.common.models import get_model
from app.common.utils import get_recorder, record, response_to_text
from app.states import MainOutputState, MainState
import logging

logger = logging.getLogger(__name__)
recorder = get_recorder()


@record
def request_parser(state: MainState):
    prefix = "[Node request_parser]"
    logger.info(f"{prefix} Start")

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
    command = response.content

    logger.info(f"{prefix} Convert '{state}' to '{command}'")
    return {"command": command}


@record
def logic_generator(state: MainState):
    prefix = "[Node logic_generator]"
    logger.info(f"{prefix} Start")

    system_message = SystemMessage(content=prompts.logic_generator_prompt)
    human_message = HumanMessage(content=state["command"])
    response = get_model("medium").invoke([system_message, human_message])
    logic = response.content

    logger.info(f"{prefix} Created logic: {logic}")
    return {"logic": logic}


@record
def handler(state: MainState):
    prefix = "[Node handler]"
    logger.info(f"{prefix} Start")

    if state["messages"]:
        logger.info(f"{prefix} Last message: {state['messages'][-1]}")

    logic = state["logic"]
    system_message = SystemMessage(content=prompts.handler_prompt.format(logic=logic))
    model = get_model("medium").bind_tools([tools.call_sql_graph, *tools.jwt_tools])
    response = model.invoke([system_message, *state["messages"]])

    logger.info(f"{prefix} Response: {response_to_text(response)}")
    return {"messages": [response]}


@record
def responser(state: MainState):
    prefix = "[Node responser]"
    logger.info(f"{prefix} Start")

    logic = state["logic"]
    system_message = SystemMessage(content=prompts.responser_prompt.format(logic=logic))
    model = get_model("medium").with_structured_output(MainOutputState)
    response = model.invoke([system_message, *state["messages"]])

    logger.info(f"{prefix} Response: {response}")
    return {"response": response}

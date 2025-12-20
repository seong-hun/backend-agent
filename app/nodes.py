import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app import prompts, tools, schemas
from app.common.models import get_model
from app.common.utils import get_api_examples, get_recorder, record, response_to_text
from app.states import MainOutputState, MainState

logger = logging.getLogger(__name__)
recorder = get_recorder()


def translator(state: MainState):
    prefix = "[Node translator]"
    logger.info(f"{prefix} Start")

    request = state["request"]
    method = request["method"]
    path = request["path"]
    query_params = request["query_params"]
    body = request["body"]

    logger.info(f"{prefix} API request:")
    logger.info(f"{prefix}   {method} /{path}")
    logger.info(f"{prefix}   query_params: {query_params}")
    logger.info(f"{prefix}   body: {body}")

    system_message = SystemMessage(content=prompts.translator_prompt)
    human_message = HumanMessage(
        content=f"""
        The user request is given by:
            method: {method},
            path: {path},
            query_params: {query_params},
            body: {body},
        """
    )
    response = (
        get_model("small")
        .with_structured_output(schemas.UserCommand)
        .invoke([system_message, human_message])
    )

    user_command = response.user_command

    logger.info(f"{prefix} Translated user request: {user_command}")

    return {"user_command": user_command}


def planner(state: MainState):
    prefix = "[Node planner]"
    logger.info(f"{prefix} Start")

    system_message = SystemMessage(
        content=prompts.planner_prompt.format(api_examples=get_api_examples())
    )
    human_message = HumanMessage(content=state["user_command"])
    response = (
        get_model("medium")
        .with_structured_output(schemas.Plan)
        .invoke([system_message, human_message])
    )

    plan = response.plan
    denied = response.denied
    denied_reason = response.denied_reason

    logger.info(f"{prefix} Generated plan:\n{plan}")

    return {
        "plan": plan,
        "denied": denied,
        "denined_reason": denied_reason,
    }


@record
def handler(state: MainState):
    prefix = "[Node handler]"
    logger.info(f"{prefix} Start")

    if state.get("messages", []) and state["messages"][-1].type == "tool":
        logger.info(f"{prefix} Tool Response: {state['messages'][-1].content}")

    system_message = SystemMessage(
        content=prompts.handler_prompt.format(plan=state["plan"])
    )
    model = get_model("medium").bind_tools(tools.handler_tools)
    response = model.invoke([system_message, *state.get("messages", [])])

    logger.info(f"{prefix} Response: {response_to_text(response)}")
    return {"messages": [response]}


@record
def responser(state: MainState):
    prefix = "[Node responser]"
    logger.info(f"{prefix} Start")

    system_message = SystemMessage(
        content=prompts.responser_prompt.format(
            user_command=state["user_command"],
            plan=state["plan"],
            api_examples=get_api_examples(),
        )
    )
    model = get_model("medium").with_structured_output(MainOutputState)
    response = model.invoke([system_message, *state["messages"]])

    logger.info(f"{prefix} Response: {response}")
    return {"response": response}

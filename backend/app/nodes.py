import logging
from datetime import datetime

from langchain_core.messages import SystemMessage

from app import prompts, tools
from app.common.models import get_model
from app.common.utils import get_api_examples, get_recorder, response_to_text
from app.obs.event_bus import event_bus
from app.schemas import Response
from app.states import MainState

logger = logging.getLogger(__name__)
recorder = get_recorder()


async def handler(state: MainState):
    prefix = "[Node handler]"
    logger.info(f"{prefix} Start")

    stage = state.get("stage")

    if stage is None:
        stage = "start"
        logger.info(f"{prefix} API request: {state['messages'][-1].content}")
        await event_bus.publish(
            {
                "type": "node",
                "graph": "main_graph",
                "name": "handler",
                "status": "start",
            },
        )

    if stage == "tool_call":
        tool_response = state["messages"][-1]
        logger.info(f"{prefix} Tool Result: {tool_response.content}")

        await event_bus.publish(
            {
                "graph": "main_graph",
                "type": "tool",
                "name": tool_response.name,
                "status": "end",
                "content": tool_response.content,
            },
        )

    system_message = SystemMessage(
        content=prompts.handler_prompt.format(api_examples=get_api_examples())
    )
    model = get_model("large")
    model_prefix = f"[{model.name}]"

    response = model.bind_tools(tools.handler_tools).invoke(
        [system_message] + state.get("messages", [])
    )

    if response.tool_calls:
        stage = "tool_call"
        logger.info(
            f"{prefix} {model_prefix} Calling a tool: {response_to_text(response)}"
        )

        for tool_call in response.tool_calls:
            await event_bus.publish(
                {
                    "graph": "main_graph",
                    "type": "tool",
                    "name": tool_call["name"],
                    "status": "start",
                    "content": tool_call["args"],
                },
            )

    elif response.content:
        stage = "end"
        logger.info(f"{prefix} {model_prefix} Final response: {response.content}")

    return {"stage": stage, "messages": [response]}


async def responder(state: MainState):
    prefix = "[Node responder]"
    logger.info(f"{prefix} Start")

    system_message = SystemMessage(
        content=prompts.responder_prompt.format(api_examples=get_api_examples())
    )
    model = get_model("medium")
    model_prefix = f"[{model.name}]"

    response = model.with_structured_output(Response).invoke(
        [system_message] + state["messages"]
    )

    logger.info(f"{prefix} {model_prefix} Response: {response}")

    logger.info(f"{prefix} API request: {state['messages'][-1].content}")

    await event_bus.publish(
        {
            "type": "node",
            "graph": "main_graph",
            "name": "responder",
            "status": "end",
            "content": response.model_dump(),
        },
    )

    return {"response": response}

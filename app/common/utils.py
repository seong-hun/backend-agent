import logging
import time
from copy import deepcopy
from functools import wraps

logger = logging.getLogger(__name__)


class Recorder:
    def __init__(self):
        self._records = []

    def record(self, node, input_state, update_state, duration, **kwargs):
        _record = {
            "node": node,
            "input_state": deepcopy(input_state),
            "update_state": deepcopy(update_state),
            "duration": duration,
            **deepcopy(kwargs),
        }

        self._records.append(_record)


recorder = Recorder()


def get_recorder():
    return recorder


def record(func):
    @wraps(func)
    def wrapper(state, **kwargs):
        start = time.time()
        update_state = func(state=state, **kwargs)
        recorder.record(
            node=func.__name__,
            input_state=state,
            update_state=update_state,
            duration=time.time() - start,
        )
        return update_state

    return wrapper


def response_to_text(response):
    if response.tool_calls:
        tool_call_texts = []
        for tool_call in response.tool_calls:
            tool_call_texts.append(
                f"Tool Call:\n\tname: {tool_call['name']}\n\targs: {tool_call['args']}"
            )
        response_text = "\n" + "\n".join(tool_call_texts)
    elif response.content:
        response_text = response.content
    else:
        response_text = response

    return response_text

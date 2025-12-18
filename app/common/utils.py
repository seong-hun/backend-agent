from copy import deepcopy
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class Recorder:
    def __init__(self):
        self._records = []

    def record(self, node, input_state, update_state, **kwargs):
        _record = {
            "node": node,
            "input_state": deepcopy(input_state),
            "update_state": deepcopy(update_state),
            **deepcopy(kwargs),
        }
        logger.info(f"=== {node} ===")
        logger.info(_record)
        self._records.append(_record)


recorder = Recorder()


def get_recorder():
    return recorder


def record(func):
    @wraps(func)
    def wrapper(state, **kwargs):
        update_state = func(state=state, **kwargs)
        recorder.record(
            node=func.__name__, input_state=state, update_state=update_state
        )
        return update_state

    return wrapper

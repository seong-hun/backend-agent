import inspect
from datetime import datetime
from functools import wraps

from app.obs.event_bus import event_bus


def state_to_dict(state):
    state_dict = {}
    for k, v in state.items():
        if k == "response":
            v = v.model_dump()
        if k == "messages":
            v = [_v.content for _v in v]

        state_dict[k] = v


def observable(node_name: str):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(state: dict):
            run_id = state["run_id"]

            state_dict = state_to_dict(state)

            await event_bus.publish(
                {
                    "node": node_name,
                    "event": "start",
                    "input": state_dict,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            if inspect.iscoroutinefunction(fn):
                result = await fn(state)
            else:
                result = fn(state)

            result_dict = state_to_dict(result)

            await event_bus.publish(
                {
                    "node": node_name,
                    "event": "end",
                    "output": result_dict,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return result

        return wrapper

    return decorator

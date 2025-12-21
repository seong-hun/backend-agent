from app import states
from app.graph import main_graph

api_request = {
    "method": "POST",
    "path": "login",
    "query_params": {},
    "body": {"username": "myuser", "password": "mypass"},
}
state = states.MainState(request=states.Request(**api_request))
output = main_graph.invoke(state)

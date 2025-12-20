from app import states
from app.graph import main_graph

api_request = {
    "method": "GET",
    "path": "users",
    "query_params": {},
    "body": {},
}
state = states.MainState(request=states.Request(**api_request))
output = main_graph.invoke(state)

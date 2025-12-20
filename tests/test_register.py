from app import states
from app.graph import main_graph

graph_input = {
    "method": "POST",
    "path": "register",
    "query_params": {},
    "body": {"username": "myuser", "password": "mypass"},
}
state = states.MainState(request=states.Request(**graph_input))
output = main_graph.invoke(state)

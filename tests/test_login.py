from app.graph import main_graph
from app.states import MainState

graph_input = {
    "method": "POST",
    "path": "login",
    "query_params": {},
    "body": {"username": "myuser", "password": "mypass"},
}
state = MainState(**graph_input)
output = main_graph.invoke(state)

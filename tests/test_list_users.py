from app.graph import main_graph
from app.states import MainState

graph_input = {
    "method": "GET",
    "path": "users",
    "query_params": {},
    "body": {},
}
state = MainState(**graph_input)
output = main_graph.invoke(state)

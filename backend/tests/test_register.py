import json

from app.graph import main_graph

output = main_graph.invoke(
    {
        "messages": [
            json.dumps(
                {
                    "method": "POST",
                    "path": "register",
                    "query_params": {},
                    "body": {"username": "myuser", "password": "mypass"},
                }
            )
        ]
    }
)

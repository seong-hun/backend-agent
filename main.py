import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import states
from app.graph import main_graph

app = FastAPI()


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(full_path: str, request: Request):
    body_bytes = await request.body()
    if body_bytes:
        body = json.loads(body_bytes.decode("utf-8"))
    else:
        body = {}

    api_request = {
        "method": request.method,
        "path": full_path,
        "query_params": dict(request.query_params),
        "body": body,
    }
    state = states.MainState(request=states.Request(**api_request))
    output = main_graph.invoke(state)

    return JSONResponse(
        status_code=output.get("status_code", 200),
        content=output.get("body", {}),
        headers=output.get("headers"),
    )

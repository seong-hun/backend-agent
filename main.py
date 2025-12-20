import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.graph import build_main_graph

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
        "headers": dict(request.headers),
    }
    main_graph = build_main_graph()
    output = main_graph.invoke({"messages": [json.dumps(api_request)]})
    response = output["response"]

    return JSONResponse(
        status_code=response.status_code,
        content=response.body,
        headers=response.headers,
    )

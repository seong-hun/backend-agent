import asyncio
import json
import logging
import uuid
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from langgraph.graph.state import RunnableConfig
from sqlalchemy import text
from sqlmodel import Session, text

from app.common.databases import db_manager
from app.graph import build_main_graph
from app.obs.event_bus import event_bus

logger = logging.getLogger("app")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/db/tables")
async def list_tables():
    tables = db_manager.list_tables()
    return {"tables": tables}


@app.get("/api/db/table/{table_name}")
async def table_snapshot(
    table_name: str, session: Session = Depends(db_manager.get_session)
):
    # validate table existence
    exists = session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"),
        {"t": table_name},
    ).first()

    if not exists:
        raise HTTPException(status_code=404, detail="table not found")

    # columns
    cols = session.execute(text(f"PRAGMA table_info({table_name})")).all()
    columns = [c[1] for c in cols]

    # rows (LIMIT enforced)
    rows = session.execute(text(f"SELECT * FROM {table_name} LIMIT 5")).mappings().all()

    return {
        "table": table_name,
        "columns": columns,
        "rows": list(rows),
        "updated_at": datetime.utcnow().isoformat(),
    }


@app.get("/runs/events")
async def stream_events():
    queue = event_bus.subscribe()

    async def event_generator():
        while True:
            data = await queue.get()
            try:
                event = f"data: {json.dumps(data)}\n\n"
                logger.info(f"Streamed: {event}")
                yield event
            except BaseException:
                breakpoint()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.api_route("/api/agent/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
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

    run_id = str(uuid.uuid4())

    async def run_graph():
        await main_graph.ainvoke(
            {"messages": [json.dumps(api_request)], "run_id": run_id}
        )

    asyncio.create_task(run_graph())
    return {"run_id": run_id}

    # response = output["response"]
    #
    # return JSONResponse(
    #     status_code=response.status_code,
    #     content=response.body,
    #     headers=response.headers,
    # )

import sqlite3
from pathlib import Path

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


def get_db():
    db_path = Path(__file__).parents[2] / "db" / "backend.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path, check_same_thread=False)

    engine = create_engine(
        "sqlite://",
        creator=lambda: conn,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    db = SQLDatabase(engine)
    return db


db = get_db()

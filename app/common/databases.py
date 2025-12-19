from pathlib import Path

from langchain_community.utilities import SQLDatabase
from sqlmodel import create_engine, inspect

import app


class DatabaseManager:
    def __init__(self, path="db/backend.db"):
        db_path = Path(path)
        if not db_path.is_absolute():
            db_path = Path(app.__path__[0]).parent / db_path

        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.db = SQLDatabase(self.engine)
        self.inspector = inspect(self.engine)

    def get_dialect(self):
        return self.db.dialect

    def get_db(self):
        return self.db

    def list_tables(self) -> list[str]:
        return self.inspector.get_table_names()

    def get_schema_text(self) -> str:
        schema_text_list = []
        for table_name in self.list_tables():
            schema_text_list.append(f"--- Schema for table: '{table_name}' ---")

            columns = self.inspector.get_columns(table_name)
            for col in columns:
                schema_text_list.append(
                    f"* Column: {col['name']} | Type: {col['type']} | Nullable: {col.get('nullable', 'N/A')}"
                )

            schema_text_list.append("")

        schema_text = "\n".join(schema_text_list)
        return schema_text


db_manager = DatabaseManager()

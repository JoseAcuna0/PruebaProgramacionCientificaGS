from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

DB_FILE = "data/database.db"
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)


def get_engine() -> Engine:
    return engine


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

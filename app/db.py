import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db/db.sqlite3")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def _ensure_schema() -> None:
    inspector = inspect(engine)
    if "transcripts" in inspector.get_table_names():
        columns = {c["name"] for c in inspector.get_columns("transcripts")}
        with engine.begin() as conn:
            if "summary" not in columns:
                conn.execute(text("ALTER TABLE transcripts ADD COLUMN summary TEXT"))
            if "summary_status" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE transcripts ADD COLUMN summary_status TEXT DEFAULT 'pending'"
                    )
                )
            if "summary_mode" not in columns:
                conn.execute(text("ALTER TABLE transcripts ADD COLUMN summary_mode TEXT"))
            if "user_id" not in columns:
                conn.execute(text("ALTER TABLE transcripts ADD COLUMN user_id INTEGER"))

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")
    result = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    summary_status = Column(String, default="pending")
    summary_mode = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    hf_token = Column(String, nullable=True)
    openai_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
_ensure_schema()

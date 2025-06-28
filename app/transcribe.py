from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import time

from .main import Base, Transcript, DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def transcribe_file(record_id: int, file_path: str):
    db = SessionLocal()
    record = db.query(Transcript).get(record_id)
    if not record:
        db.close()
        return
    record.status = "processing"
    db.commit()
    # Placeholder transcription logic
    time.sleep(2)  # simulate work
    record.status = "completed"
    record.result = f"Transcribed text for {os.path.basename(file_path)}"
    db.commit()
    db.close()

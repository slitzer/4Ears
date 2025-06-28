from fastapi import FastAPI, Request, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .db import SessionLocal, Transcript
import shutil
import os


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data")

from .transcribe import transcribe_file

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    db = SessionLocal()
    files = db.query(Transcript).order_by(Transcript.created_at.desc()).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "files": files})

@app.post("/upload", response_class=HTMLResponse)
def upload_file(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    db = SessionLocal()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    record = Transcript(filename=file.filename)
    db.add(record)
    db.commit()
    db.refresh(record)
    background_tasks.add_task(transcribe_file, record.id, file_path)
    db.close()
    return templates.TemplateResponse("upload_success.html", {"request": request, "filename": file.filename})

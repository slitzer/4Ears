from fastapi import FastAPI, Request, UploadFile, File, BackgroundTasks, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from .db import SessionLocal, Transcript, User
import shutil
import os


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data")

from .transcribe import transcribe_file, summarize_record

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "change-me"))
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    db = SessionLocal()
    user = db.query(User).get(user_id)
    db.close()
    return user

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    query = db.query(Transcript)
    if user:
        query = query.filter(Transcript.user_id == user.id)
    files = query.order_by(Transcript.created_at.desc()).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "files": files, "user": user})

@app.post("/upload", response_class=HTMLResponse)
def upload_file(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    db = SessionLocal()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    user = get_current_user(request)
    record = Transcript(filename=file.filename, user_id=user.id if user else None)
    db.add(record)
    db.commit()
    db.refresh(record)
    background_tasks.add_task(transcribe_file, record.id, file_path)
    db.close()
    return templates.TemplateResponse("upload_success.html", {"request": request, "filename": file.filename, "file_id": record.id})

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    if user and pwd_context.verify(password, user.password_hash):
        request.session["user_id"] = user.id
        db.close()
        return RedirectResponse("/", status_code=302)
    db.close()
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
def register(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        db.close()
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username taken"})
    user = User(username=username, password_hash=pwd_context.hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    db.close()
    return RedirectResponse("/", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

@app.get("/settings", response_class=HTMLResponse)
def settings_form(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("settings.html", {"request": request, "user": user})

@app.post("/settings", response_class=HTMLResponse)
def settings_save(request: Request, hf_token: str = Form(""), openai_token: str = Form("")):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    db = SessionLocal()
    db_user = db.query(User).get(user.id)
    db_user.hf_token = hf_token
    db_user.openai_token = openai_token
    db.commit()
    db.refresh(db_user)
    db.close()
    return templates.TemplateResponse("settings.html", {"request": request, "user": db_user, "success": True})


@app.get("/status/{file_id}")
def status(file_id: int):
    db = SessionLocal()
    record = db.query(Transcript).get(file_id)
    if not record:
        db.close()
        return {"status": "unknown"}
    status = record.status
    db.close()
    return {"status": status}


@app.get("/download/{file_id}")
def download_text(file_id: int):
    db = SessionLocal()
    record = db.query(Transcript).get(file_id)
    if not record or not record.result:
        db.close()
        return RedirectResponse("/", status_code=302)
    text = record.result
    filename = f"{record.filename}.txt"
    db.close()
    return Response(text, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.post("/summarize/{file_id}")
def summarize(file_id: int, background_tasks: BackgroundTasks, mode: str = Form("basic_summary")):
    db = SessionLocal()
    record = db.query(Transcript).get(file_id)
    if not record or not record.result:
        db.close()
        return RedirectResponse("/", status_code=302)
    if record.summary_status == "processing":
        db.close()
        return RedirectResponse("/", status_code=302)
    background_tasks.add_task(summarize_record, record.id, mode)
    db.close()
    return RedirectResponse("/", status_code=302)

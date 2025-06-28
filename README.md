# 4Ears

# WhisperX Transcription Service

A self-hosted transcription web app powered by WhisperX. Upload audio/video files, get transcripts, and browse your history — all via Docker Compose.

## 🛠️ Tech Stack

- **Backend**: FastAPI  
- **Transcription**: WhisperX  
- **Frontend**: Jinja2 + Bootstrap  
- **Storage**: Local filesystem + SQLite  
- **Containerization**: Docker, Docker Compose  

## 🚀 Features

- Upload audio/video (wav, mp3, m4a, mp4, mkv)  
- Real-time transcription with speaker diarization  
- List, view & download past transcripts  
- Configurable WhisperX models via environment  
- Deployable with a single `docker-compose up`  

## 🗂️ Project Structure



├── docker-compose.yml # service definitions
├── Dockerfile # builds the FastAPI image
├── .env # HF_TOKEN, MODEL_SIZE, etc.
├── README.md # this file
└── app
├── main.py # FastAPI entrypoint + routing
├── transcribe.py # WhisperX logic (adapted)
├── models.py # SQLAlchemy models
├── templates
│ └── index.html # upload form + history table
├── static
│ └── style.css # custom styles
├── data # uploaded files & outputs
└── db.sqlite3 # SQLite database


## 🛠️ Installation & Usage

1. **Clone the repo**  

Configure environment

cp .env.example .env
# Edit .env to add your HF_TOKEN (if using diarization)


Launch with Docker Compose

docker-compose up -d
Access the app
Navigate to http://localhost:7210

Upload & Transcribe

Click Choose File to pick an audio/video file

Hit Upload & Transcribe

Watch progress, then view/download transcripts

Your history lives in the table below

📥 Docker Compose


🧭 Roadmap
Live Recording Applet

Browser-based mic selector + user metadata (username, session name)

Chunk audio every 5–10 minutes (or on size threshold)

Auto-upload chunks to server & enqueue for transcription

WebSocket or SSE for real-time status updates

Multi-User Support

Handle 8–10 simultaneous recording/transcription sessions

Per-user workspace & history

Optional authentication (OAuth/JWT)

Meeting Recorder Mode

“Meeting” project type: single file + multi-speaker diarization

Automatic chunk splitting to avoid huge uploads

Bulk download ZIP of transcripts and audio

Scaling & Resilience

Redis or RabbitMQ queue for transcription jobs

Optional GPU support for faster WhisperX runs

Docker Swarm/Kubernetes manifests for horizontal scaling

UX & Misc

Themable skins, for DnD or work meetings

User landing page with uploadable artwork, etc..

Drag-and-drop upload area

Dark mode toggle bu default (because midnight sessions)

Mobile-responsive layout for on-the-go transcriptions

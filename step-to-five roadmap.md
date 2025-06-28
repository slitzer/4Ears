🚧 Phase 1 – Nail the MVP (1–2 weeks)
Project scaffold

Spin up FastAPI + Jinja2 boilerplate

Hook in WhisperX inside transcribe.py

SQLite + SQLAlchemy models for File, User, Transcript

File upload & history

Single-page form (Bootstrap) to upload audio/video

Save to app/data/ and insert DB record

Background task (FastAPI’s BackgroundTasks) to run WhisperX

Poll or live-update status via simple AJAX

Dockerize

Write Dockerfile (Python 3.10, install FFmpeg, WhisperX deps)

Compose file exposing port 7210, volume-mount app/data + DB

Smoke-test “upload → transcribe → view” loop

🎙 Phase 2 – Live Recording Applet (2–3 weeks)
WebRTC front-end

JS mic selector + record API (MediaRecorder)

Chunk every 5 minutes (or 10 MB) into Blob files

Chunk delivery & queue

POST chunks to /api/record endpoint with metadata (username, session)

FastAPI writes chunk → DB job queue table

Transcription queue groundwork

MVP: polling table and BackgroundTasks still okay

Hook in WebSocket/SSE to push “chunk 5/12 done” updates

👥 Phase 3 – Multi-User & Auth (1–2 weeks)
User accounts

Add simple JWT/OAuth (e.g. Auth0 or FastAPI Users)

Isolate user data folders and history views

Workspace isolation

“Campaigns” or “Meetings” table

Link files & recordings to campaign_id + user_id

Clean UI to switch contexts

⚙️ Phase 4 – Robust Queue & Scaling (2–3 weeks)
Real queue broker

Swap out background tasks for Celery + Redis or RabbitMQ

Define Celery tasks for WhisperX runs

GPU support

Detect GPU availability in container (nvidia-docker)

ENV toggle USE_GPU=true

Compose → Swarm/K8s

Add Docker Stack file (labels, healthchecks)

Optional K8s manifests (Deployments, PVCs for data)

🎨 Phase 5 – Polish & UX (1–2 weeks)
Drag-and-drop upload with progress bar

Dark/light theme switch

Campaign-specific artwork uploads

ZIP export of multi-chunk transcripts + audio

Mobile responsive tweaks


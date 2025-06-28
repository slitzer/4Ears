# 4Ears

**4Ears** is a lightweight web interface for generating transcripts using [WhisperX](https://github.com/m-bain/whisperX). Upload audio or video files, let the server transcribe them, and browse previous results – all contained in a simple Docker setup.

## Features

- Upload `wav`, `mp3`, `m4a`, `mp4`, `mkv` and other common formats
- Background transcription with optional speaker diarization
- View the status and result of each uploaded file
- Runs entirely in Docker with a single `docker-compose up`

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and adjust values if needed  
   - `HF_TOKEN` – optional token for models requiring authentication
   - `MODEL_SIZE` – WhisperX model size (e.g. `small`)
   - `DATABASE_URL` – connection string for the SQLite database
3. Launch the stack with Docker Compose:

   ```bash
   docker-compose up -d
   ```

4. Visit `http://localhost:7210` in your browser and start uploading files.

Uploaded media and transcripts are stored under `app/data` with metadata in `db.sqlite3`. The web interface lists every past transcription and allows downloading the generated text.

## Project Layout

```
docker-compose.yml  # service definitions
Dockerfile          # application container
app/
├── main.py         # FastAPI application
├── transcribe.py   # placeholder transcription logic
├── templates/      # Jinja2 HTML templates
└── static/         # CSS files
```

## Roadmap

The project is in early stages. Planned improvements include:

- Live recording directly from the browser
- Multi-user support with optional authentication
- A proper job queue for WhisperX processing
- GPU acceleration and horizontal scaling
- A polished UI with drag-and-drop uploads and mobile support

Contributions and feedback are welcome!

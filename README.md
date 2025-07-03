# 4Ears

**4Ears** is a lightweight web interface for generating transcripts and summaries. It uses [WhisperX](https://github.com/m-bain/whisperX) for speech-to-text and can optionally send the transcript to an LLM (OpenAI or local) for summarization.

## Features

- Upload `wav`, `mp3`, `m4a`, `mp4`, `mkv` and other common formats
- Background transcription with optional speaker diarization
- Timestamped output with speaker labels when a Hugging Face token is provided
- Optional summaries via OpenAI or a local LLM
- View the status and result of each uploaded file
- Runs entirely in Docker with a single `docker-compose up`

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and adjust values if needed  
   - `HF_TOKEN` – optional token for Hugging Face models, used to enable speaker diarization
   - `MODEL_SIZE` – WhisperX model size (e.g. `small`)
   - `DATABASE_URL` – connection string for the SQLite database
   - `OPENAI_API_KEY` – optional key for OpenAI summarization
   - `SUMMARIZATION_ENGINE` – `openai` or `ollama`
   - `OLLAMA_URL` and `OLLAMA_MODEL` – endpoint and model name for local summarization (when using `ollama`)
3. Create a directory named `db` for the SQLite database then launch the stack with Docker Compose:

   ```bash
   mkdir -p db
   docker-compose up -d
   ```

4. Visit `http://localhost:7210` in your browser and start uploading files.

Uploaded media and transcripts are stored under `app/data` with metadata in `db/db.sqlite3`. The web interface lists every past transcription and allows downloading the generated text.

If an `OPENAI_API_KEY` is provided (or a local Ollama server is configured) you can request summaries for completed transcripts directly from the UI. Choose one of the summary modes and the server will queue the job in the background.

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

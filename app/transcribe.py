import os
import logging
import tempfile
import shutil

from pydub import AudioSegment
import whisperx

from .db import Transcript, DATABASE_URL, SessionLocal

logger = logging.getLogger(__name__)

def _convert_to_wav(path: str, temp_dir: str) -> str:
    """Convert input audio to wav if necessary and return new path."""
    if path.lower().endswith(".wav"):
        return path
    wav_path = os.path.join(temp_dir, "audio.wav")
    audio = AudioSegment.from_file(path)
    audio.export(wav_path, format="wav")
    return wav_path


def _run_whisperx(wav_path: str) -> str:
    model = whisperx.load_model("base", device="cpu", compute_type="float32")
    result = model.transcribe(wav_path, batch_size=16)
    segments = result.get("segments", [])
    return " ".join(s.get("text", "") for s in segments)


def transcribe_file(record_id: int, file_path: str) -> None:
    db = SessionLocal()
    record = db.query(Transcript).get(record_id)
    if not record:
        db.close()
        return

    record.status = "processing"
    db.commit()

    temp_dir = tempfile.mkdtemp(prefix="transcribe_")
    try:
        wav_path = _convert_to_wav(file_path, temp_dir)
        text = _run_whisperx(wav_path)
        record.status = "completed"
        record.result = text
        db.commit()
    except Exception as exc:
        logger.exception("Transcription failed")
        record.status = "failed"
        record.result = str(exc)
        db.commit()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        db.close()

import os
import logging
import tempfile
import shutil

from pydub import AudioSegment
import whisperx

from .db import Transcript, SessionLocal, User
from .summarize import summarize

logger = logging.getLogger(__name__)

def _convert_to_wav(path: str, temp_dir: str) -> str:
    """Convert input audio to wav if necessary and return new path."""
    if path.lower().endswith(".wav"):
        return path
    wav_path = os.path.join(temp_dir, "audio.wav")
    audio = AudioSegment.from_file(path)
    audio.export(wav_path, format="wav")
    return wav_path


def _run_whisperx(wav_path: str, hf_token: str | None = None) -> str:
    """Run WhisperX with optional diarization and return timestamped text."""

    # Load ASR model
    model = whisperx.load_model("base", device="cpu", compute_type="float32")

    # Transcribe audio
    result = model.transcribe(wav_path, batch_size=16)

    # Align words to improve timestamps
    model_a, metadata = whisperx.load_align_model(language_code="en", device="cpu")
    result = whisperx.align(result["segments"], model_a, metadata, wav_path, device="cpu")

    # Perform speaker diarization if token provided
    if hf_token:
        try:
            diarize_model = whisperx.diarize.DiarizationPipeline(use_auth_token=hf_token, device="cpu")
            diarize_segments = diarize_model(wav_path)
            result = whisperx.assign_word_speakers(diarize_segments, result)
        except AttributeError:
            # Older versions of whisperx do not have diarization
            logger.warning("DiarizationPipeline not available; skipping diarization")

    segments = result.get("segments", [])
    lines = []
    for seg in segments:
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        text = seg.get("text", "")
        speaker = seg.get("speaker")
        if speaker is not None:
            lines.append(f"[{start:.2f}s - {end:.2f}s] Speaker {speaker}: {text}")
        else:
            lines.append(f"[{start:.2f}s - {end:.2f}s] {text}")

    return "\n".join(lines)


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
        user = db.query(User).get(record.user_id) if record.user_id else None
        hf_token = (
            user.hf_token if user and user.hf_token else os.getenv("HF_TOKEN", "")
        )
        text = _run_whisperx(wav_path, hf_token or None)
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


def summarize_record(record_id: int, mode: str) -> None:
    db = SessionLocal()
    record = db.query(Transcript).get(record_id)
    if not record or not record.result:
        db.close()
        return

    record.summary_status = "processing"
    record.summary_mode = mode
    db.commit()

    try:
        text = record.result
        user = db.query(User).get(record.user_id) if record.user_id else None
        openai_token = (
            user.openai_token if user and user.openai_token else os.getenv("OPENAI_API_KEY")
        )
        summary = summarize(text, mode, openai_api_key=openai_token)
        record.summary_status = "completed"
        record.summary = summary
        db.commit()
    except Exception as exc:
        logger.exception("Summarization failed")
        record.summary_status = "failed"
        record.summary = str(exc)
        db.commit()
    finally:
        db.close()

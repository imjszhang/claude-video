"""Minimal OpenAI-compatible Whisper API backed by faster-whisper."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI(title="watch-local-whisper")

MODEL_NAME = os.environ.get("WHISPER_MODEL", "base")
DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")
THREADS = int(os.environ.get("WHISPER_THREADS", "4"))

_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        _model = WhisperModel(
            MODEL_NAME,
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
            cpu_threads=THREADS,
        )
    return _model


@app.get("/v1/models")
def list_models():
    return {"object": "list", "data": [{"id": "whisper-1", "object": "model"}]}


@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form("whisper-1"),
    response_format: str = Form("json"),
    temperature: str = Form("0"),
):
    del model  # base model is fixed in WHISPER_MODEL
    suffix = Path(file.filename or "audio.mp3").suffix or ".mp3"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    try:
        whisper = _get_model()
        segments_iter, info = whisper.transcribe(
            path,
            temperature=float(temperature or 0),
        )
        segments = []
        texts: list[str] = []
        for seg in segments_iter:
            text = seg.text.strip()
            if not text:
                continue
            segments.append({"start": seg.start, "end": seg.end, "text": text})
            texts.append(text)
        full = " ".join(texts).strip()
        if response_format == "verbose_json":
            return {
                "text": full,
                "segments": segments,
                "language": info.language,
            }
        return {"text": full}
    finally:
        Path(path).unlink(missing_ok=True)

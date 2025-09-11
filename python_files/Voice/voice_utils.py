import os, tempfile, torch
import streamlit as st

@st.cache_resource(show_spinner=False)
def load_stt(model_size: str | None = None):
    """
    Load OpenAI Whisper once and cache it.
    Sizes: tiny, base, small, medium, large. Default: 'base'.
    Set env WHISPER_SIZE=small if you have GPU.
    """
    import whisper
    size = model_size or os.environ.get("WHISPER_SIZE", "base")
    return whisper.load_model(size)

def transcribe_audio_bytes(audio_bytes: bytes, model) -> str:
    """
    Persist bytes to a temp .wav and transcribe via Whisper.
    Returns a plain text transcript ('' on failure).
    """
    if not audio_bytes:
        return ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        result = model.transcribe(tmp_path, fp16=torch.cuda.is_available())
        return (result.get("text") or "").strip()
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

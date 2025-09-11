# ------------------------------------------------------------
# EmpathyBot Streamlit UI (text input + mic button + badges)
# All paths under /content/sample_data
# ------------------------------------------------------------
import sys, json, time, uuid, inspect, os, tempfile
from pathlib import Path
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# ---------- Module path (DIRECTORY, not the .py file) ----------
MODULE_DIR = "/content/sample_data"
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

# ---------- Import your core pipeline & helpers ----------
import empathybot_sprint_py as core
from empathybot_sprint_py import respond as core_respond, emo_pipe, vstore, llm
from voice_utils import load_stt, transcribe_audio_bytes
from ui_utils import emotion_badge_html

# ---------- Robust ROOT/DATA paths ----------
try:
    ROOT = Path(__file__).resolve().parent
except NameError:
    ROOT = Path(MODULE_DIR).resolve()

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FEEDBACK_LOG = DATA_DIR / "feedback.jsonl"

# Your corpus path (in sample_data)
CORPUS_CLEAN = Path("/content/sample_data/corpus_clean.json")

# ---------- Adapter: call your respond() without changing its signature ----------
def respond_adapter(user_text: str, tone: str = "warm"):
    try:
        out = core_respond(user_text, emo_pipe=emo_pipe, vstore=vstore, llm=llm, tone=tone)
    except TypeError:
        try:
            out = core_respond(user_text, tone=tone)
        except TypeError:
            out = core_respond(user_text)
    if isinstance(out, str):
        out = {"reply": out}
    return {
        "emotion": out.get("emotion") or out.get("detected_emotion") or "",
        "confidence": out.get("confidence"),
        "bucket": out.get("bucket") or "",
        "templates": out.get("templates") or [],
        "reply": out.get("reply") or "",
        "prompt": out.get("prompt", None),
    }

# ---------- Page setup & decorative styles ----------
st.set_page_config(page_title="EmpathyBot — Emotion-Aware RAG", page_icon="🤝", layout="wide")
st.markdown("""
<style>
:root {
  --bg1: #fdf2f8; --bg2: #eef2ff; --bg3: #ecfeff;
  --card-bg: rgba(255,255,255,0.75); --card-br: rgba(148,163,184,0.35);
  --shadow: 0 10px 30px rgba(2,6,23,0.10); --muted: #64748b;
  --primaryA: #a78bfa; --primaryB: #60a5fa;
}
html, body, .stApp { background: linear-gradient(135deg, var(--bg1), var(--bg2), var(--bg3)); background-attachment: fixed; }
.card { background: var(--card-bg); border:1px solid var(--card-br); border-radius:18px; padding:14px 16px; box-shadow:var(--shadow); backdrop-filter: blur(8px); }
h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
  background: linear-gradient(90deg, var(--primaryA), var(--primaryB));
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.small { color: var(--muted); font-size: 12px }
.stButton > button {
  border:0; background:linear-gradient(135deg,var(--primaryA),var(--primaryB));
  color:white; font-weight:600; padding:.55rem .9rem; border-radius:12px; box-shadow:var(--shadow);
}
.stButton > button:hover { filter:brightness(1.05); transform: translateY(-1px); transition:.15s all ease-in-out; }
.stTextInput > div > div > input {
  background:rgba(255,255,255,0.85)!important; border:1px solid var(--card-br)!important;
  border-radius:12px!important; box-shadow:var(--shadow)!important; height: 3rem;
}
.mic-btn > button {
  width: 3rem; height: 3rem; border-radius: 999px; padding: 0; font-size: 1.1rem; font-weight: 700;
  background: linear-gradient(135deg, #ef4444, #f97316);
}
.mic-btn > button:hover { filter: brightness(1.05); transform: translateY(-1px); }
.chat-bubble-user { background:linear-gradient(135deg,#d1fae5,#a7f3d0); border:1px solid #34d399; border-radius:18px; padding:12px 16px; margin-bottom:12px; box-shadow:var(--shadow);}
.chat-bubble-bot  { background:linear-gradient(135deg,#ede9fe,#dbeafe); border:1px solid #a5b4fc;  border-radius:18px; padding:12px 16px; margin-bottom:12px; box-shadow:var(--shadow);}
</style>
""", unsafe_allow_html=True)

st.title("🤝 EmpathyBot — Emotion-Aware RAG")
st.caption("Type your message or click the mic to speak. We detect emotion, retrieve empathetic templates, and compose a concise reply with a safety disclaimer.")

# ---------- Sidebar ----------
with st.sidebar:
    st.subheader("⚙️ Settings")
    tone = st.selectbox("Tone", ["warm", "concise", "practical", "celebratory"], index=0)
    st.markdown("---")
    st.markdown("### 📁 Corpus")
    if CORPUS_CLEAN.exists():
        try:
            items = json.loads(CORPUS_CLEAN.read_text(encoding="utf-8"))
            st.markdown(f"Loaded **{len(items)}** cleaned templates from:")
            st.code(str(CORPUS_CLEAN), language="text")
        except Exception as e:
            st.warning(f"Could not read corpus: {e}")
    else:
        st.error("Cleaned corpus not found at /content/sample_data/corpus_clean.json")
    st.markdown("---")
    st.markdown("### 🔌 Modules")
    st.write("Using models loaded in:", MODULE_DIR)
    st.write("Module file:", Path(inspect.getfile(core)).as_posix())

# ---------- Session state ----------
if "chat" not in st.session_state:
    st.session_state.chat = []
if "user_text" not in st.session_state:
    st.session_state.user_text = ""
if "show_recorder" not in st.session_state:
    st.session_state.show_recorder = False

# ---------- Input row: text input + mic + send ----------
col1, col2, col3 = st.columns([7,1,1], gap="small")
with col1:
    st.session_state.user_text = st.text_input(
        "Message",
        value=st.session_state.user_text,
        placeholder="Tell me what's going on…",
        label_visibility="collapsed",
        key="msg_input",
    )
with col2:
    if st.button("🎙️", key="mic_toggle", help="Record with microphone", type="secondary"):
        st.session_state.show_recorder = not st.session_state.show_recorder
with col3:
    send_clicked = st.button("Send", type="primary")

# Recorder appears only when toggled ON
if st.session_state.show_recorder:
    st.markdown("<div class='card'>Click the mic once to start, again to stop. We’ll transcribe and fill the text box.</div>", unsafe_allow_html=True)
    audio_bytes = audio_recorder(
        text="Start / Stop Recording",
        recording_color="#f43f5e",
        neutral_color="#94a3b8",
        icon_size="2x",
    )
    if audio_bytes:
        with st.spinner("Transcribing…"):
            stt_model = load_stt()  # env WHISPER_SIZE or 'base'
            transcript = transcribe_audio_bytes(audio_bytes, stt_model)
        if transcript:
            st.session_state.user_text = transcript
            st.success("Transcribed! You can edit the text and click Send.")
            st.session_state.show_recorder = False
            st.rerun()
        else:
            st.error("Couldn’t get a transcript. Please try again.")

# Click Send -> run pipeline
if send_clicked:
    text = (st.session_state.user_text or "").strip()
    if not text:
        st.warning("Please type a message or use the mic to record.")
    else:
        with st.spinner("Thinking empathetically…"):
            out = respond_adapter(text, tone=tone)
        st.session_state.chat.append(("user", text))
        st.session_state.chat.append(("bot", out))
        st.session_state.user_text = ""
        st.rerun()

# ---------- History & feedback ----------
for role, payload in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'><b>You</b><br>{payload}</div>", unsafe_allow_html=True)
    else:
        label  = payload.get("emotion", "")
        conf   = payload.get("confidence")
        bucket = payload.get("bucket", "")
        st.markdown(emotion_badge_html(label, bucket, conf), unsafe_allow_html=True)

        st.markdown(f"<div class='chat-bubble-bot'>{payload.get('reply','')}</div>", unsafe_allow_html=True)

        if payload.get("templates"):
            with st.expander("Show retrieved templates"):
                for i, t in enumerate(payload["templates"], 1):
                    st.markdown(f"- **{i}.** {t}")

        if payload.get("prompt"):
            with st.expander("Debug: final prompt"):
                st.code(payload["prompt"])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("👍 Helpful", key=f"up_{uuid.uuid4()}"):
                FEEDBACK_LOG.open("a", encoding="utf-8").write(
                    json.dumps({
                        "ts": time.time(), "user": "",
                        "reply": payload.get("reply",""),
                        "emotion": payload.get("emotion",""),
                        "bucket": payload.get("bucket",""),
                        "helpful": True,
                        "templates": payload.get("templates", [])
                    }) + "\n"
                )
                st.toast("Thanks for the feedback!")
        with c2:
            if st.button("👎 Not helpful", key=f"down_{uuid.uuid4()}"):
                FEEDBACK_LOG.open("a", encoding="utf-8").write(
                    json.dumps({
                        "ts": time.time(), "user": "",
                        "reply": payload.get("reply",""),
                        "emotion": payload.get("emotion",""),
                        "bucket": payload.get("bucket",""),
                        "helpful": False,
                        "templates": payload.get("templates", [])
                    }) + "\n"
                )
                st.toast("Thanks—logged for improvement.")

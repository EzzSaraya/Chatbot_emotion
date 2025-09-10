# ------------------------------------------------------------
# Streamlit UI for EmpathyBot using your existing module code.
# No function logic is redefined here: we import and use them.
# ------------------------------------------------------------
import sys, json, time, uuid, inspect
from pathlib import Path
import streamlit as st

# ---------- Module path (DIRECTORY, not the .py file) ----------
MODULE_DIR = "/content/EmpathyBot"   # adjust if different
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

# Import your module & key symbols (use globals built inside your module)
import empathybot_sprint_py as core
from empathybot_sprint_py import respond as core_respond, emo_pipe, vstore, llm

# ---------- Robust ROOT/DATA paths (works in Streamlit or notebook) ----------
try:
    ROOT = Path(__file__).resolve().parent
except NameError:
    # In notebooks, __file__ is not defined; fall back to the module's folder
    ROOT = Path(MODULE_DIR).resolve()

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FEEDBACK_LOG = DATA_DIR / "feedback.jsonl"

# Your corpus path (as requested)
CORPUS_CLEAN = Path("/content/EmpathyBot/corpus_clean.json")

# ---------- Small adapter: call your respond() with best-guess signature ----------
def respond_adapter(user_text: str, tone: str = "warm"):
    """
    Try multiple call signatures so we don't have to modify your module.
    Normalizes result to a dict with keys we use in UI.
    """
    try:
        out = core_respond(user_text, emo_pipe=emo_pipe, vstore=vstore, llm=llm, tone=tone)
    except TypeError:
        try:
            out = core_respond(user_text, tone=tone)
        except TypeError:
            out = core_respond(user_text)

    if isinstance(out, str):  # normalize if your respond returns a string
        out = {"reply": out}

    # normalize common keys
    out_norm = {
        "emotion": out.get("emotion") or out.get("detected_emotion") or "",
        "confidence": out.get("confidence"),
        "bucket": out.get("bucket") or "",
        "templates": out.get("templates") or [],
        "reply": out.get("reply") or "",
        "prompt": out.get("prompt", None),
    }
    return out_norm

# ---------- UI Theme / Styles ----------
st.set_page_config(page_title="EmpathyBot — Emotion-Aware RAG", page_icon="🤝", layout="wide")

st.markdown("""
<style>
/* ---------- Decorative theme palette ---------- */
:root {
  --bg1: #fdf2f8;   /* pink-50 */
  --bg2: #eef2ff;   /* indigo-50 */
  --bg3: #ecfeff;   /* cyan-50 */
  --card-bg: rgba(255,255,255,0.75);
  --card-br: rgba(148,163,184,0.35);
  --shadow: 0 10px 30px rgba(2,6,23,0.10);
  --muted: #64748b;

  --primaryA: #a78bfa; /* violet-400 */
  --primaryB: #60a5fa; /* blue-400 */
  --accentA:  #34d399; /* emerald-400 */
  --accentB:  #f472b6; /* pink-400 */
}

/* App background gradient */
html, body, .stApp {
  background: linear-gradient(135deg, var(--bg1), var(--bg2), var(--bg3));
  background-attachment: fixed;
}

/* Cards / containers */
.card {
  background: var(--card-bg);
  border: 1px solid var(--card-br);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

/* Headings */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
  background: linear-gradient(90deg, var(--primaryA), var(--primaryB));
  -webkit-background-clip: text; background-clip: text;
  color: transparent;
}

/* Badges */
.badge {
  display:inline-block; padding:6px 12px; border-radius:999px;
  font-size:12px; background: linear-gradient(135deg, #eef2ff, #e9d5ff);
  color:#4338CA; border:1px solid rgba(99,102,241,0.25);
  box-shadow: var(--shadow);
}
.emobadge {
  padding:6px 12px; border-radius:12px; font-size:12px;
  background: linear-gradient(135deg, #f5f3ff, #e0f2fe);
  border:1px solid rgba(148,163,184,0.35);
  box-shadow: var(--shadow);
}

/* Chat bubbles */
.chat-bubble-user {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0); /* mint gradient */
  border: 1px solid #34d399;
  border-radius: 18px; padding: 12px 16px; margin-bottom: 12px;
  box-shadow: var(--shadow);
}
.chat-bubble-bot {
  background: linear-gradient(135deg, #ede9fe, #dbeafe); /* lavender/blue gradient */
  border: 1px solid #a5b4fc;
  border-radius: 18px; padding: 12px 16px; margin-bottom: 12px;
  box-shadow: var(--shadow);
}

/* Small muted text */
.small { color: var(--muted); font-size: 12px }

/* Buttons */
.stButton > button {
  border: 0;
  background: linear-gradient(135deg, var(--primaryA), var(--primaryB));
  color: white; font-weight: 600;
  padding: 0.6rem 1rem; border-radius: 12px;
  box-shadow: var(--shadow);
}
.stButton > button:hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
  transition: all .15s ease-in-out;
}

/* Inputs */
textarea, .stTextArea textarea {
  background: rgba(255,255,255,0.85)!important;
  border: 1px solid var(--card-br)!important;
  border-radius: 12px!important;
  box-shadow: var(--shadow)!important;
}

/* Expanders */
.streamlit-expanderHeader {
  background: linear-gradient(90deg, rgba(167,139,250,0.15), rgba(96,165,250,0.15));
  border-radius: 10px;
  border: 1px solid var(--card-br);
}
</style>
""", unsafe_allow_html=True)

st.title("🤝 EmpathyBot — Emotion-Aware RAG")
st.caption("Detect emotion → retrieve empathetic templates → compose a natural reply with a safety disclaimer.")

# ---------- Sidebar controls ----------
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
        st.error("Cleaned corpus not found at /content/EmpathyBot/corpus_clean.json")

    st.markdown("---")
    st.markdown("### 🔌 Modules")
    st.write("Using models loaded in:", MODULE_DIR)
    st.write("Module file:", Path(inspect.getfile(core)).as_posix())

# ---------- Chat UI ----------
if "chat" not in st.session_state:
    st.session_state.chat = []

col_left, col_right = st.columns([2,1], gap="large")

with col_right:
    st.markdown("#### Tips")
    st.markdown("""
<div class="card">
<ul>
<li>Try: <i>“I’m overwhelmed and sad.”</i>, <i>“I’m furious about this.”</i></li>
<li>Adjust <b>Tone</b> to change the vibe.</li>
<li>This app uses your prebuilt <code>emo_pipe</code> / <code>vstore</code> / <code>llm</code> from the module.</li>
</ul>
</div>
""", unsafe_allow_html=True)
    # Small model info (optional)
    with st.expander("Show module details"):
        st.write("`emo_pipe`:", type(emo_pipe).__name__)
        st.write("`vstore`:", type(vstore).__name__)
        st.write("`llm`:", type(llm).__name__)

with col_left:
    user_text = st.text_area("Your message", placeholder="Tell me what's going on…", height=120)
    if st.button("Send", type="primary") and user_text.strip():
        with st.spinner("Thinking empathetically…"):
            out = respond_adapter(user_text, tone=tone)
        # append to chat history
        st.session_state.chat.append(("user", user_text))
        st.session_state.chat.append(("bot", out))

# ---------- History & feedback ----------
for role, payload in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'><b>You</b><br>{payload}</div>", unsafe_allow_html=True)
    else:
        label = payload.get("emotion", "")
        conf = payload.get("confidence")
        bucket = payload.get("bucket", "")
        badge_text = f"detected: {label}" + (f" ({conf})" if conf is not None else "") + (f" → {bucket}" if bucket else "")
        st.markdown(f"<span class='emobadge'>{badge_text}</span>", unsafe_allow_html=True)

        st.markdown(f"<div class='chat-bubble-bot'>{payload.get('reply','')}</div>", unsafe_allow_html=True)

        # retrieved templates
        if payload.get("templates"):
            with st.expander("Show retrieved templates"):
                for i, t in enumerate(payload["templates"], 1):
                    st.markdown(f"- **{i}.** {t}")

        # optional: show final prompt if you returned it (useful for debugging)
        if payload.get("prompt"):
            with st.expander("Debug: final prompt"):
                st.code(payload["prompt"])

        # feedback buttons
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

# 🤝 EmpathyBot — Emotion-Aware RAG with Few-Shot Prompting (Text + Voice)

EmpathyBot detects a user’s **emotion**, retrieves **empathetic response templates** with RAG, and composes a natural reply via a **few-shot LLM**.  
It ships with a clean **Streamlit UI**, supports **voice input (speech-to-text)** via a single inline mic, and includes safety guardrails (neutral fallback, crisis filters, disclaimer). For easy sharing, it works with **ngrok** or **Cloudflare** tunnels.

> **Pipeline:** Emotion detector → FAISS retrieval (MiniLM) → Few-shot reply → Safety disclaimer  
> **Input:** Type in the box **or** click the mic to speak (Whisper STT)

---
![EmpathyBot UI — single online mic & emotion badges](assets/empathybot-hero.png)


## 🎬 Demo
**👉 [Watch the demo on Google Drive](https://drive.google.com/file/d/1u-yY6Cl6LbNom7zlt4zYr2L4I9eaTksi/view?usp=drive_link)**

What you’ll see:
- Emotion badge + confidence
- Top-3 retrieved templates (transparent RAG)
- Tone switcher (warm / concise / practical / celebratory)
- **Text + Voice input** (single mic next to “Send”)
- Safety disclaimer in every reply
- Feedback logging (👍 / 👎)

---

## ✨ Features
- **Text *and* Voice input**
  - Inline mic beside **Send** (no extra bar); click to record, click again to stop.
  - **Whisper** converts speech → text and auto-fills the input.
- **Emotion detection** → 4 buckets: `happiness | sadness | anger | neutral`
- **Advanced RAG retrieval** using **FAISS** + **MiniLM** embeddings with emotion filtering
- **Few-shot generation** (FLAN-T5) with post-processing to avoid repetition/parroting
- **Safety layer**: neutral fallback on low confidence; crisis/profanity screening; disclaimer
- **Streamlit UI**: per-emotion color badges, template inspection, tone control, feedback logging
- **Colab-friendly sharing**: ngrok or Cloudflare tunnel

---

## 🧠 Models Used
- **Emotion Detector:** `bhadresh-savani/distilbert-base-uncased-emotion`  
  DistilBERT fine-tuned for granular emotions (joy/sadness/anger/etc.).
- **RAG Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`  
  Lightweight (384-d) and fast for template retrieval.
- **Generator (Few-Shot):** `google/flan-t5-base`  
  Instruction-tuned; produces concise, polite replies (wrapped with LangChain `HuggingFacePipeline`).
- **Speech-to-Text:** **OpenAI Whisper** (`base` by default)  
  Robust multilingual STT (requires `ffmpeg`). Configure size via `WHISPER_SIZE=tiny|base|small|medium|large`.
- **Vector Store:** **FAISS**  
  In-memory similarity search with persisted index files.

---

## 🧩 How It Works
1. **Detect** emotion for the message (or transcript), map to `happiness|sadness|anger|neutral`.
2. **Retrieve** top templates aligned with that emotion (FAISS + MiniLM + metadata filter).
3. **Compose** a 1–2 sentence empathetic reply via a few-shot prompt (FLAN-T5).
4. **Guardrails**: dedup & cleanup; neutral fallback if confidence is low; append a safety disclaimer.

---

## 🧰 LangChain Usage
- **Embeddings:** `HuggingFaceEmbeddings` (MiniLM)  
- **Vector store:** `langchain_community.vectorstores.FAISS` (+ emotion metadata)  
- **Retriever:** similarity search (optional MMR variant available)  
- **Prompting:** compact few-shot `PromptTemplate` (tone-aware)  
- **LLM wrapper:** `HuggingFacePipeline` for `.invoke()` API

---





## 📁 Project structure
Chatbot_emotion/
├─ Data/
│ ├─ corpus.json
│ ├─ corpus_clean.json
│ ├─ faiss.index
│ ├─ faiss_meta.pkl
│ ├─ tweet_eval_emotion_clean.csv
│ └─ tweet_eval_emotion_clean.parquet
├─ python_files/
│ ├─ voice/
│   ├─ voice_utils.py 
│    └─ ui_utils.py 
│ ├─ empathybot_sprint_py.py
│ ├─ server.py
│ └─ streamlit_app.py
├─ requirements.txt
└─ README.md


Author : **Ezz Eldin Saraya**

# 🤝 EmpathyBot — Emotion-Aware RAG with Few-Shot Prompting

EmpathyBot detects the user's **emotion**, retrieves **empathetic response templates** with RAG, and composes a natural reply via a **few-shot LLM**. It ships with a clean **Streamlit UI**, supports **ngrok** for quick sharing, and includes safety guardrails (neutral fallback, crisis filters, disclaimer).

>
>   
> Emotion detector → FAISS retrieval (MiniLM) → FLAN-T5 few-shot reply → safety disclaimer.  
> One-click web UI via Streamlit; public URL via ngrok.

---

## ✨ Features

- **Emotion detection** (e.g., joy/sadness/anger → mapped to 4 buckets)
- **RAG retrieval** using FAISS + MiniLM embeddings
- **Few-shot generation**  with anti-repetition + post-processing
- **Safety layer**: neutral fallback when low confidence; crisis/profanity filtering; disclaimer
- **Streamlit app** with tone control, template inspection, and feedback logging
- **ngrok integration** for quick secure sharing (Colab-friendly)

---

## 🧩 How it works

1. **Detect** emotion for the user message and map to one of: `happiness | sadness | anger | neutral`.
2. **Retrieve** top templates aligned with that emotion using FAISS (with on-topic filtering).
3. **Compose** a short, supportive reply using a few-shot prompt (FLAN-T5).
4. **Guardrails**: post-process to remove meta/instructions and append a disclaimer.

---

## 📁 Project structure


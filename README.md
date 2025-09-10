# 🤝 EmpathyBot — Emotion-Aware RAG with Few-Shot Prompting

EmpathyBot detects the user's **emotion**, retrieves **empathetic response templates** with RAG, and composes a natural reply via a **few-shot LLM**. It ships with a clean **Streamlit UI**, supports **ngrok** for quick sharing, and includes safety guardrails (neutral fallback, crisis filters, disclaimer).

>
>   
> Emotion detector → FAISS retrieval (MiniLM) →  few-shot reply → safety disclaimer.  
> One-click web UI via Streamlit; public URL via ngrok.



## 🎬 Want to watch a Demo?

Click to watch (2–5 min walkthrough):

**👉 [Watch the demo on Google Drive](https://drive.google.com/file/d/1Y9mNihtPWmcDMREB7tuegfeUZ2OxJflj/view?usp=sharing)**

What you’ll see:
- Emotion detection badge + confidence
- Top-3 retrieved templates (transparent RAG)
- Tone switcher (warm / concise / practical / celebratory)
- Safety disclaimer in every reply
- Feedback logging (👍 / 👎)

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


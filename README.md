# 🎙️ VoiceForge — Enterprise Text-to-Speech Platform

> Convert any English text into professional-quality **320 kbps MP3** audio using
> OpenAI `tts-1-hd` and Groq PlayAI voices. Supports plain text input and `.txt` file upload.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

| Feature | Detail |
|---|---|
| **Dual TTS Providers** | OpenAI `tts-1-hd` and Groq `playai-tts` |
| **Professional Male Voices** | Onyx, Echo, Fritz, Chip, Mason, Thunder, Basil… |
| **320 kbps MP3 Output** | FFmpeg re-encode via `pydub` for studio quality |
| **Unlimited Text Length** | Sentence-aware chunking handles books, reports, articles |
| **File Upload** | Drag-and-drop `.txt` up to 5 MB |
| **Speed Control** | 0.5× – 2.0× speech rate |
| **Analytics Dashboard** | Session-level conversion tracking, provider usage, history |
| **Encrypted Secrets** | API keys stored in Streamlit Secrets — never in source code |

---

## 🏗️ Architecture

```
voiceforge/
├── app.py                    # Streamlit entry point
├── src/
│   ├── config.py             # AppConfig — secrets loading, voice catalogue
│   ├── tts_engine.py         # TTSEngine — OpenAI & Groq synthesis
│   ├── text_processor.py     # Clean, stats, sentence-aware chunking
│   ├── audio_utils.py        # pydub merge + 320kbps re-encode
│   ├── analytics.py          # Session analytics + dashboard
│   └── ui_components.py      # CSS injection, render blocks
├── .streamlit/
│   ├── config.toml           # Dark theme, upload limits
│   └── secrets.toml          # ← LOCAL ONLY, gitignored
├── .env.example              # Template for local env vars
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start — Local (macOS / Ubuntu)

### Prerequisites

**macOS**
```bash
brew install python@3.11 ffmpeg
```

**Ubuntu / Debian**
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv ffmpeg
```

> `ffmpeg` is required by `pydub` for MP3 merging and 320 kbps re-encoding.
> The app works without it (byte-concat fallback) but audio quality may suffer on long texts.

---

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/voiceforge.git
cd voiceforge
```

### 2. Create a virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows (not officially supported)
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys (two options)

#### Option A — Streamlit secrets (recommended for parity with cloud)

Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-..."
GROQ_API_KEY   = "gsk_..."
```
> This file is already in `.gitignore`. Never commit it.

#### Option B — Environment variables

```bash
cp .env.example .env
# Edit .env with your actual keys
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."
```

You only need **one** provider's key to use the app. The unused provider will show an error only if selected.

### 5. Run the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## ☁️ Deploy to Streamlit Cloud

### 1. Push to GitHub

```bash
git add .
git commit -m "feat: initial VoiceForge"
git push origin main
```

> Ensure `.gitignore` is present — it blocks `.env` and `secrets.toml` from being committed.

### 2. Create a new Streamlit Cloud app

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your GitHub repo and branch
4. Set **Main file path** → `app.py`
5. Click **Advanced settings**

### 3. Add secrets (encrypted at rest by Streamlit)

In **Advanced settings → Secrets**, paste:

```toml
OPENAI_API_KEY = "sk-..."
GROQ_API_KEY   = "gsk_..."
```

Click **Save**. Streamlit Cloud encrypts these values — they are never visible in logs or source.

### 4. Deploy

Click **Deploy**. Streamlit will build the environment and launch your app at a public URL.

> **ffmpeg on Streamlit Cloud:** Streamlit Cloud does not include ffmpeg by default.
> Add a `packages.txt` file to your repo root to install it:

```
# packages.txt
ffmpeg
```

---

## 🔑 API Keys

| Provider | Where to get | Env var |
|---|---|---|
| OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | `OPENAI_API_KEY` |
| Groq | [console.groq.com/keys](https://console.groq.com/keys) | `GROQ_API_KEY` |

Both providers offer free tiers suitable for testing.

---

## 🎙️ Voice Reference

### OpenAI (`tts-1-hd`)

| Voice ID | Description |
|---|---|
| `onyx` | Deep, authoritative male — best for narration & reports |
| `echo` | Clear, professional male — ideal for corporate content |
| `fable` | Warm, engaging male — great for storytelling |
| `alloy` | Balanced, neutral — versatile all-rounder |

### Groq (PlayAI)

| Voice ID | Description |
|---|---|
| `Fritz-PlayAI` | Crisp German-English male |
| `Chip-PlayAI` | Confident US male |
| `Mason-PlayAI` | Smooth US male |
| `Thunder-PlayAI` | Bold, resonant male |
| `Basil-PlayAI` | British professional male |
| `Angelo-PlayAI` | Clear, articulate male |

---

## ⚙️ Configuration

All settings live in `src/config.py`:

```python
MAX_CHARS  = 100_000   # Max characters per conversion
CHUNK_SIZE = 4_096     # Chars per API call (OpenAI limit)
MAX_FILE_SIZE_MB = 5   # Upload limit
```

Streamlit server settings are in `.streamlit/config.toml`.

---

## 🔒 Security Model

```
Local Dev                       Streamlit Cloud
─────────────────────           ─────────────────────────────────
.streamlit/secrets.toml  ──▶   Settings → Secrets (AES-256 at rest)
    OR
.env (not committed)
    ↓                               ↓
src/config.py reads via         st.secrets["KEY"] (same API)
st.secrets → os.getenv()
```

**Never:**
- Hardcode API keys in source files
- Commit `.env` or `secrets.toml`
- Log API keys to console or Streamlit output

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## 📦 Packages

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `openai` | OpenAI TTS API (`tts-1-hd`) |
| `groq` | Groq TTS API (PlayAI) |
| `pydub` | Audio segment merge + encode |
| `pandas` | Analytics dataframes |
| `python-dotenv` | `.env` loading for local dev |
| `ffmpeg` (system) | MP3 encode/decode backend for pydub |

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

## 🤝 Contributing

PRs welcome. Open an issue first for large changes.

---

*Built with Python 3.11 · Streamlit · OpenAI · Groq*

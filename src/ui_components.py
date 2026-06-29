"""
VoiceForge UI Components — CSS, output card, about page.
"""

import streamlit as st
from src.audio_utils import AudioUtils


class UIComponents:

    @staticmethod
    def inject_css():
        st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.sidebar-logo { font-size:28px; font-weight:700; color:#6C63FF; letter-spacing:-0.5px; }
.sidebar-tagline { font-size:12px; color:#888; margin-top:-8px; }

.main-title {
    font-size:42px; font-weight:800;
    background: linear-gradient(135deg,#6C63FF 0%,#48CAE4 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.main-subtitle { color:#888; font-size:15px; margin-bottom:24px; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#6C63FF,#48CAE4) !important;
    border:none !important; border-radius:8px !important;
    font-weight:600 !important; font-size:15px !important;
    transition:opacity 0.2s !important;
}
.stButton > button[kind="primary"]:hover { opacity:0.88 !important; }

.voice-card {
    background:#1a1a2e; border:1px solid #2d2d4e;
    border-radius:8px; padding:10px 14px; margin-top:8px; margin-bottom:4px;
}

.vf-output-card {
    background:linear-gradient(135deg,#0f0f1a 0%,#1a1a2e 100%);
    border:1px solid #6C63FF55; border-radius:14px; padding:24px;
}

.empty-state {
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    height:280px; border:2px dashed #2d2d4e; border-radius:14px;
    color:#555; text-align:center; padding:32px;
}

.badge {
    display:inline-block; padding:3px 10px; border-radius:999px;
    font-size:11px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase;
}
.badge-green  { background:#00c46622; color:#00c466; border:1px solid #00c46644; }
.badge-purple { background:#6C63FF22; color:#9d97ff; border:1px solid #6C63FF44; }
.badge-blue   { background:#48CAE422; color:#48CAE4; border:1px solid #48CAE444; }
.badge-orange { background:#FF9F4322; color:#FF9F43; border:1px solid #FF9F4344; }

.stDownloadButton > button {
    background:#00c466 !important; color:white !important;
    border:none !important; border-radius:8px !important;
    font-weight:700 !important; font-size:15px !important;
    transition:opacity 0.2s !important;
}
.stDownloadButton > button:hover { opacity:0.85 !important; }
</style>
""", unsafe_allow_html=True)

    @staticmethod
    def render_empty_state():
        st.markdown("""
<div class="empty-state">
    <div style="font-size:52px;margin-bottom:12px;">🎙️</div>
    <div style="font-size:16px;font-weight:600;color:#666;margin-bottom:6px;">Ready to synthesise</div>
    <div style="font-size:13px;color:#444;">
        Select a voice, enter text, and click<br><strong>Generate Audio</strong>
    </div>
</div>""", unsafe_allow_html=True)

    @staticmethod
    def render_audio_output(result: dict):
        audio_bytes = result["audio"]
        size_label  = AudioUtils.format_size(len(audio_bytes))
        indian_badge = '<span class="badge badge-orange">🇮🇳 Indian accent</span> ' if result.get("indian") else ""

        st.markdown(f"""
<div class="vf-output-card">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap;">
    <span style="font-size:20px;">✅</span>
    <span style="font-weight:700;font-size:15px;">Audio Ready</span>
    <span class="badge badge-green">320 kbps</span>
    <span class="badge badge-purple">MP3</span>
    {indian_badge}
  </div>
""", unsafe_allow_html=True)

        st.audio(audio_bytes, format="audio/mp3")

        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Provider**\n\n{result['provider']}")
        m2.markdown(f"**Model**\n\n`{result['model']}`")
        m3.markdown(f"**Size**\n\n{size_label}")

        voice_label = result.get("voice_label", result.get("voice_id", ""))
        st.markdown(
            f"<small style='color:#555;'>Voice: {voice_label} · "
            f"Chars: {result['chars']:,} · Chunks: {result['chunks']}</small>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")
        st.download_button(
            label=f"⬇️  Download MP3  ({size_label})",
            data=audio_bytes,
            file_name=result["filename"],
            mime="audio/mpeg",
            use_container_width=True,
        )

    @staticmethod
    def render_about(config):
        from src.config import VOICE_GROUPS, VOICE_CATALOGUE

        st.markdown("### About VoiceForge")
        st.markdown("""
Enterprise-grade text-to-speech that converts any English text into professional-quality
**320 kbps MP3** audio. Supports plain text input, `.txt` upload, and a curated voice catalogue
spanning professional male English voices and casual Indian female voices.
---
#### Voice Catalogue
""")
        for group_name, gdata in VOICE_GROUPS.items():
            st.markdown(f"**{group_name}**")
            if "note" in gdata:
                st.caption(gdata["note"])
            rows = []
            for vid in gdata["voices"]:
                m = VOICE_CATALOGUE[vid]
                rows.append(f"| `{vid}` | {m['label']} | `{m['model']}` | {'🇮🇳 Yes' if m.get('indian') else '—'} |")
            st.markdown("| Voice ID | Description | Model | Indian accent |")
            st.markdown("|---|---|---|---|")
            for r in rows:
                st.markdown(r)
            st.markdown("")

        st.markdown("---")
        st.markdown("""
#### Indian Accent Strategy

Neither OpenAI `tts-1-hd` nor Groq Orpheus expose dedicated Indian-accent voice IDs.
VoiceForge uses **OpenAI `gpt-4o-mini-tts`** for the three Indian female voices — this model
accepts an `instructions` parameter that steers accent, cadence, and tone.
Each voice has a distinct accent persona baked into its instructions:

| Voice | Accent persona |
|---|---|
| Nova | Warm, friendly South-Asian; Mumbai/Bengaluru professional |
| Shimmer | Bright, energetic; Delhi/Hyderabad urban |
| Coral | Soft, measured; Chennai/Pune educated |

#### Security

API keys are loaded from **Streamlit Secrets** (cloud) or **environment variables** (local).
They are never hardcoded and never committed to git.

#### Architecture
- **Frontend:** Streamlit + custom CSS dark theme
- **TTS:** OpenAI `tts-1-hd` / `gpt-4o-mini-tts` · Groq `canopylabs/orpheus-v1-english`
- **Audio pipeline:** multi-chunk merge via `pydub` + FFmpeg → 320 kbps MP3
- **Text processing:** Unicode normalisation + sentence-aware chunking
""")
        st.caption("VoiceForge v1.1.0 · Arkadip Basu · 2025")

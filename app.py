"""
VoiceForge — Enterprise Text-to-Speech Platform
Main Streamlit application
"""

import streamlit as st
import os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from src.config import AppConfig, VOICE_CATALOGUE, VOICE_GROUPS
from src.tts_engine import TTSEngine
from src.text_processor import TextProcessor
from src.audio_utils import AudioUtils
from src.ui_components import UIComponents
from src.analytics import Analytics

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VoiceForge TTS",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
UIComponents.inject_css()

# ─── Init ─────────────────────────────────────────────────────────────────────
config    = AppConfig()
analytics = Analytics()

@st.cache_resource
def get_tts_engine():
    return TTSEngine(config)

tts_engine = get_tts_engine()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🎙️ VoiceForge</div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-tagline">Enterprise Text-to-Speech</p>', unsafe_allow_html=True)
    st.subheader("arkadipbasu.github.io")
    st.divider()

    st.markdown("### 🎙️ Voice Selection")

    # Build flat list grouped with section headers for selectbox
    voice_options_flat  = []   # (display_label, voice_id)
    group_header_ids    = set()

    for group_name, gdata in VOICE_GROUPS.items():
        voice_options_flat.append((f"── {group_name} ──", "__HEADER__"))
        group_header_ids.add(f"── {group_name} ──")
        for vid in gdata["voices"]:
            meta  = VOICE_CATALOGUE[vid]
            voice_options_flat.append((meta["label"], vid))

    labels = [x[0] for x in voice_options_flat]
    ids    = [x[1] for x in voice_options_flat]

    # Default selection: first real voice (skip the first header)
    default_idx = next(i for i, vid in enumerate(ids) if vid != "__HEADER__")

    sel_idx = st.selectbox(
        "Choose voice",
        options=range(len(labels)),
        format_func=lambda i: labels[i],
        index=default_idx,
        label_visibility="collapsed",
    )

    # If a header was selected, nudge to next real voice
    selected_voice_id = ids[sel_idx]
    if selected_voice_id == "__HEADER__":
        for j in range(sel_idx + 1, len(ids)):
            if ids[j] != "__HEADER__":
                selected_voice_id = ids[j]
                break

    selected_meta = VOICE_CATALOGUE[selected_voice_id]

    # Voice info card
    provider_badge = "🟢 OpenAI" if selected_meta["provider"] == "OpenAI" else "🟣 Groq"
    indian_badge   = " 🇮🇳 Indian accent" if selected_meta.get("indian") else ""
    style_badge    = "👔 Professional" if selected_meta["style"] == "professional" else "💬 Casual"
    gender_badge   = "♂ Male" if selected_meta["gender"] == "male" else "♀ Female"

    st.markdown(
        f"""<div class="voice-card">
        <div style="font-size:12px;color:#aaa;margin-bottom:6px;">{provider_badge} · {style_badge} · {gender_badge}{indian_badge}</div>
        <div style="font-size:11px;color:#666;">Model: <code>{selected_meta['model']}</code></div>
        </div>""",
        unsafe_allow_html=True,
    )

    if selected_meta.get("indian"):
        st.info("🇮🇳 Accent steering is active for this voice via OpenAI instructions parameter.", icon="ℹ️")

    st.divider()
    st.markdown("### ⚙️ Audio Settings")
    speed = st.slider("Speech Speed", 0.5, 2.0, 1.0, 0.05, help="0.5× slower — 2.0× faster")

    st.divider()
    st.markdown("### 📊 Session Stats")
    stats = analytics.get_session_stats()
    c1, c2 = st.columns(2)
    c1.metric("Runs", stats["total_conversions"])
    c2.metric("Chars", f"{stats['total_chars']:,}")

    st.divider()
    st.caption("VoiceForge v1.1.0 · Enterprise TTS")

# ─── Main ─────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">🎙️ VoiceForge</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">Enterprise TTS · Professional male · Casual Indian female · 320 kbps MP3</p>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["📝 Convert", "📈 Dashboard", "ℹ️ About"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — CONVERT
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    col_main, col_out = st.columns([3, 2], gap="large")

    with col_main:
        st.markdown("### Input")
        input_method = st.radio(
            "Input method", ["✏️ Type / Paste", "📁 Upload .txt"],
            horizontal=True, label_visibility="collapsed"
        )

        raw_text = ""
        if "✏️" in input_method:
            raw_text = st.text_area(
                "Text", height=280,
                placeholder="Paste any text — articles, scripts, reports, emails…\nSupports up to 100,000 characters.",
                label_visibility="collapsed",
            )
        else:
            up = st.file_uploader("Upload .txt", type=["txt"], help="UTF-8, up to 5 MB")
            if up:
                try:
                    raw_text = up.read().decode("utf-8")
                    st.success(f"✅ **{up.name}** — {len(raw_text):,} characters loaded")
                    with st.expander("Preview", expanded=False):
                        st.text(raw_text[:2000] + ("…" if len(raw_text) > 2000 else ""))
                except Exception as e:
                    st.error(f"Failed to read file: {e}")

        if raw_text.strip():
            proc  = TextProcessor(raw_text)
            stats_row = proc.get_stats()
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Characters", f"{stats_row['chars']:,}")
            s2.metric("Words",      f"{stats_row['words']:,}")
            s3.metric("Sentences",  f"{stats_row['sentences']:,}")
            s4.metric("Est. Time",  stats_row['est_duration'])
            if stats_row['chars'] > config.MAX_CHARS:
                st.warning("⚠️ Text exceeds 100k chars — will be chunked automatically.")

        st.markdown("---")
        btn_col, info_col = st.columns([1, 2])
        with btn_col:
            go = st.button("🎙️ Generate Audio", type="primary",
                           use_container_width=True, disabled=not raw_text.strip())
        with info_col:
            voice_short = selected_meta["label"].split("·")[0].strip()
            st.markdown(
                f'<p style="color:#888;font-size:13px;margin-top:10px;">Voice: <b>{voice_short}</b> · 320 kbps MP3</p>',
                unsafe_allow_html=True,
            )

    with col_out:
        st.markdown("### Output")

        if "audio_result" not in st.session_state:
            UIComponents.render_empty_state()

        if go and raw_text.strip():
            with st.spinner("🎙️ Synthesising…"):
                try:
                    processor   = TextProcessor(raw_text)
                    chunks      = processor.chunk(config.CHUNK_SIZE)
                    progress    = st.progress(0, text="Initialising…")
                    audio_parts = []

                    for i, chunk in enumerate(chunks):
                        progress.progress(
                            (i + 1) / len(chunks),
                            text=f"Chunk {i+1}/{len(chunks)}…"
                        )
                        audio_parts.append(
                            tts_engine.synthesise(
                                text=chunk,
                                voice_id=selected_voice_id,
                                speed=speed,
                            )
                        )

                    progress.progress(1.0, text="Merging → 320 kbps MP3…")
                    final_audio = AudioUtils.merge_and_encode(audio_parts, bitrate="320k")
                    filename    = f"voiceforge_{selected_voice_id}.mp3"

                    st.session_state.audio_result = {
                        "audio":    final_audio,
                        "filename": filename,
                        "voice_id": selected_voice_id,
                        "voice_label": selected_meta["label"],
                        "provider": selected_meta["provider"],
                        "model":    selected_meta["model"],
                        "indian":   selected_meta.get("indian", False),
                        "chars":    len(processor.clean()),
                        "chunks":   len(chunks),
                    }
                    analytics.record_conversion(
                        provider=selected_meta["provider"],
                        voice_id=selected_voice_id,
                        chars=len(processor.clean()),
                        chunks=len(chunks),
                        indian=selected_meta.get("indian", False),
                    )
                    progress.empty()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Conversion failed: {e}")
                    st.exception(e)

        if "audio_result" in st.session_state:
            UIComponents.render_audio_output(st.session_state.audio_result)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📈 Analytics Dashboard")
    analytics.render_dashboard()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — ABOUT
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    UIComponents.render_about(config)

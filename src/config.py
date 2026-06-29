"""
VoiceForge Configuration
Handles secrets from Streamlit Cloud secrets.toml or local .env

Voice catalogue (June 2026):
  OpenAI  — tts-1-hd  : onyx, echo, fable, alloy (male)
            gpt-4o-mini-tts: nova, shimmer, coral, sage (female, steerable accent via instructions)
  Groq    — canopylabs/orpheus-v1-english : daniel, troy, austin (male), autumn, diana, hannah (female)
            playai-tts still listed for legacy; migrated to Orpheus on GroqCloud.

Indian accent strategy:
  Neither OpenAI tts-1-hd nor Groq Orpheus expose dedicated Indian-accent voice IDs.
  For OpenAI we use gpt-4o-mini-tts (supports accent-steering via `instructions`) with
  nova / shimmer / coral voices. For Groq we use autumn / diana / hannah (warm female).
  The TTS engine injects accent instructions for voices tagged as Indian.
"""

import os
import streamlit as st


# ─── Voice metadata ────────────────────────────────────────────────────────────
# Each entry: voice_id → {label, gender, style, indian, instructions (optional)}
# `indian=True` triggers accent-steering instructions in the TTS engine.

VOICE_CATALOGUE: dict[str, dict] = {

    # ── OpenAI professional male ─────────────────────────────────────────────
    "onyx": {
        "label":        "Onyx ♂ · Deep, authoritative male",
        "provider":     "OpenAI",
        "model":        "tts-1-hd",
        "gender":       "male",
        "style":        "professional",
        "indian":       False,
    },
    "echo": {
        "label":        "Echo ♂ · Clear, professional male",
        "provider":     "OpenAI",
        "model":        "tts-1-hd",
        "gender":       "male",
        "style":        "professional",
        "indian":       False,
    },

    # ── OpenAI casual Indian female (accent-steered via gpt-4o-mini-tts) ────
    "nova": {
        "label":        "Nova ♀ · Casual Indian female · Warm & friendly",
        "provider":     "OpenAI",
        "model":        "gpt-4o-mini-tts",
        "gender":       "female",
        "style":        "casual",
        "indian":       True,
        "instructions": (
            "Speak with a natural Indian English accent — a warm, educated South-Asian tone. "
            "Keep the delivery friendly and conversational, like a young professional from Mumbai or Bengaluru. "
            "Maintain a moderate, pleasant pace."
        ),
    },
    "shimmer": {
        "label":        "Shimmer ♀ · Casual Indian female · Bright & expressive",
        "provider":     "OpenAI",
        "model":        "gpt-4o-mini-tts",
        "gender":       "female",
        "style":        "casual",
        "indian":       True,
        "instructions": (
            "Speak with a natural Indian English accent — bright, expressive, and energetic, "
            "like a confident young woman from Delhi or Hyderabad. "
            "Sound spontaneous and conversational, with natural rhythmic cadence."
        ),
    },
    "coral": {
        "label":        "Coral ♀ · Casual Indian female · Soft & approachable",
        "provider":     "OpenAI",
        "model":        "gpt-4o-mini-tts",
        "gender":       "female",
        "style":        "casual",
        "indian":       True,
        "instructions": (
            "Speak with a gentle Indian English accent — soft, warm, and approachable, "
            "like a calm, articulate woman from Chennai or Pune. "
            "Use a measured pace with natural Indian intonation patterns."
        ),
    },

    # ── Groq / Orpheus professional male ────────────────────────────────────
    "daniel": {
        "label":        "Daniel ♂ · Deep, professional male",
        "provider":     "Groq",
        "model":        "canopylabs/orpheus-v1-english",
        "gender":       "male",
        "style":        "professional",
        "indian":       False,
    },
    "troy": {
        "label":        "Troy ♂ · Confident, resonant male",
        "provider":     "Groq",
        "model":        "canopylabs/orpheus-v1-english",
        "gender":       "male",
        "style":        "professional",
        "indian":       False,
    },

    # ── Groq / Orpheus casual female (warm English; closest to Indian cadence) ─
    "autumn": {
        "label":        "Autumn ♀ · Casual female · Warm & natural",
        "provider":     "Groq",
        "model":        "canopylabs/orpheus-v1-english",
        "gender":       "female",
        "style":        "casual",
        "indian":       False,   # Orpheus doesn't support instructions; labelled warm casual
    },
    "diana": {
        "label":        "Diana ♀ · Casual female · Clear & friendly",
        "provider":     "Groq",
        "model":        "canopylabs/orpheus-v1-english",
        "gender":       "female",
        "style":        "casual",
        "indian":       False,
    },
    "hannah": {
        "label":        "Hannah ♀ · Casual female · Bright & expressive",
        "provider":     "Groq",
        "model":        "canopylabs/orpheus-v1-english",
        "gender":       "female",
        "style":        "casual",
        "indian":       False,
    },
}

# ─── Grouped view used by the UI ──────────────────────────────────────────────
VOICE_GROUPS = {
    "👔 Professional Male (English)": {
        "voices":   ["onyx", "echo", "daniel", "troy"],
        "providers": {"onyx": "OpenAI", "echo": "OpenAI", "daniel": "Groq", "troy": "Groq"},
    },
    "🇮🇳 Casual Indian Female (accent-steered)": {
        "voices":   ["nova", "shimmer", "coral"],
        "providers": {"nova": "OpenAI", "shimmer": "OpenAI", "coral": "OpenAI"},
        "note": "Uses OpenAI gpt-4o-mini-tts with accent instructions. Realistic Indian cadence.",
    },
    "💬 Casual Female (English)": {
        "voices":   ["autumn", "diana", "hannah"],
        "providers": {"autumn": "Groq", "diana": "Groq", "hannah": "Groq"},
        "note": "Groq Orpheus warm English female voices.",
    },
}


class AppConfig:
    """Centralised configuration — reads from st.secrets (cloud) or env (local)."""

    # ─── Limits ─────────────────────────────────────────────────────────────────
    MAX_CHARS        = 100_000
    CHUNK_SIZE       = 4_096
    MAX_FILE_SIZE_MB = 5

    # ─── Provider list ───────────────────────────────────────────────────────────
    AVAILABLE_PROVIDERS = ["OpenAI", "Groq"]

    # ─── Default voice per provider ─────────────────────────────────────────────
    DEFAULT_VOICE = {"OpenAI": "onyx", "Groq": "daniel"}

    # ─── Expose catalogue at instance level ─────────────────────────────────────
    VOICE_CATALOGUE = VOICE_CATALOGUE
    VOICE_GROUPS    = VOICE_GROUPS

    def __init__(self):
        self._openai_key = None
        self._groq_key   = None
        self._load_secrets()

    def _load_secrets(self):
        """Load API keys — Streamlit Cloud first, then env vars."""
        try:
            self._openai_key = st.secrets["OPENAI_API_KEY"]
        except (KeyError, FileNotFoundError):
            self._openai_key = os.getenv("OPENAI_API_KEY", "")

        try:
            self._groq_key = st.secrets["GROQ_API_KEY"]
        except (KeyError, FileNotFoundError):
            self._groq_key = os.getenv("GROQ_API_KEY", "")

    @property
    def openai_api_key(self) -> str:
        return self._openai_key or ""

    @property
    def groq_api_key(self) -> str:
        return self._groq_key or ""

    def validate_voice(self, voice_id: str) -> tuple[bool, str]:
        """Return (ok, error_message) — checks provider key availability."""
        meta = VOICE_CATALOGUE.get(voice_id)
        if not meta:
            return False, f"Unknown voice: {voice_id}"
        provider = meta["provider"]
        if provider == "OpenAI" and not self._openai_key:
            return False, "OpenAI API key not configured. Add OPENAI_API_KEY to secrets."
        if provider == "Groq" and not self._groq_key:
            return False, "Groq API key not configured. Add GROQ_API_KEY to secrets."
        return True, ""

    def voice_meta(self, voice_id: str) -> dict:
        return VOICE_CATALOGUE.get(voice_id, {})

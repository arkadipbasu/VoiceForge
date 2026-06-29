"""
VoiceForge TTS Engine
Routes synthesis to OpenAI (tts-1-hd / gpt-4o-mini-tts) or Groq (Orpheus).

Indian accent voices use OpenAI gpt-4o-mini-tts with an `instructions` field
that steers accent, cadence, and tone toward a natural Indian-English delivery.
"""

import io
import streamlit as st
from src.config import AppConfig, VOICE_CATALOGUE


class TTSEngine:
    """Unified interface for OpenAI and Groq TTS providers."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._openai_client = None
        self._groq_client   = None

    # ─── Lazy clients ─────────────────────────────────────────────────────────

    def _get_openai(self):
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=self.config.openai_api_key)
        return self._openai_client

    def _get_groq(self):
        if self._groq_client is None:
            from groq import Groq
            self._groq_client = Groq(api_key=self.config.groq_api_key)
        return self._groq_client

    # ─── Public API ───────────────────────────────────────────────────────────

    def synthesise(self, text: str, voice_id: str, speed: float = 1.0) -> bytes:
        """
        Convert text to raw MP3 bytes using the provider/model tied to voice_id.
        Raises ValueError on misconfiguration; propagates API errors.
        """
        ok, err = self.config.validate_voice(voice_id)
        if not ok:
            raise ValueError(err)
        if not text.strip():
            raise ValueError("Empty text passed to TTS engine.")

        meta = VOICE_CATALOGUE[voice_id]
        provider = meta["provider"]

        if provider == "OpenAI":
            return self._synthesise_openai(text, voice_id, meta, speed)
        elif provider == "Groq":
            return self._synthesise_groq(text, voice_id, meta, speed)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    # ─── OpenAI ───────────────────────────────────────────────────────────────

    def _synthesise_openai(self, text: str, voice_id: str, meta: dict, speed: float) -> bytes:
        client = self._get_openai()
        model  = meta["model"]           # tts-1-hd or gpt-4o-mini-tts

        kwargs = dict(
            model=model,
            voice=voice_id,
            input=text,
            speed=max(0.25, min(speed, 4.0)),   # OpenAI clamps 0.25–4.0
            response_format="mp3",
        )

        # Accent-steering: only gpt-4o-mini-tts supports `instructions`
        if meta.get("indian") and meta.get("instructions") and model == "gpt-4o-mini-tts":
            kwargs["instructions"] = meta["instructions"]

        response = client.audio.speech.create(**kwargs)
        return response.content

    # ─── Groq / Orpheus ───────────────────────────────────────────────────────

    def _synthesise_groq(self, text: str, voice_id: str, meta: dict, speed: float) -> bytes:
        client = self._get_groq()
        model  = meta["model"]           # canopylabs/orpheus-v1-english

        response = client.audio.speech.create(
            model=model,
            voice=voice_id,
            input=text,
            speed=max(0.5, min(speed, 5.0)),    # Orpheus range 0.5–5.0
            response_format="mp3",
        )

        if hasattr(response, "content"):
            return response.content

        # Fallback streaming collect
        buf = io.BytesIO()
        for chunk in response.iter_bytes():
            buf.write(chunk)
        return buf.getvalue()

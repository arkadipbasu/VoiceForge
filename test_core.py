"""
VoiceForge — Unit Tests  (v1.1.0)
Run: pytest tests/ -v
"""

import pytest
from src.text_processor import TextProcessor
from src.audio_utils import AudioUtils
from src.config import AppConfig, VOICE_CATALOGUE, VOICE_GROUPS


# ─── TextProcessor ────────────────────────────────────────────────────────────

class TestTextProcessor:

    def test_stats_basic(self):
        tp = TextProcessor("Hello world. This is a test.")
        s  = tp.get_stats()
        assert s["words"] == 6
        assert s["chars"] > 0
        assert any(c in s["est_duration"] for c in ("s", "m"))

    def test_clean_removes_control_chars(self):
        cleaned = TextProcessor("Hello\x00 World\x01").clean()
        assert "\x00" not in cleaned and "Hello" in cleaned

    def test_clean_normalises_quotes(self):
        cleaned = TextProcessor("\u201CHello\u201D it\u2019s great").clean()
        assert '"Hello"' in cleaned and "it's" in cleaned

    def test_chunk_single(self):
        chunks = TextProcessor("Short text.").chunk(max_chars=4096)
        assert chunks == ["Short text."]

    def test_chunk_splits_long_text(self):
        text   = ("This is sentence number one. This is sentence number two. " * 3)
        chunks = TextProcessor(text).chunk(max_chars=60)
        assert len(chunks) > 1
        for c in chunks:
            assert len(c) <= 65  # slight tolerance for word overrun

    def test_chunk_no_empty(self):
        for c in TextProcessor("A. B. C. D. E.").chunk(max_chars=10):
            assert c.strip()


# ─── AudioUtils ───────────────────────────────────────────────────────────────

class TestAudioUtils:

    def test_format_bytes(self):
        assert AudioUtils.format_size(512) == "512 B"

    def test_format_kb(self):
        assert "KB" in AudioUtils.format_size(2048)

    def test_format_mb(self):
        assert "MB" in AudioUtils.format_size(2 * 1024 * 1024)

    def test_concat_fallback(self):
        assert AudioUtils._concat_fallback([b"AA", b"BB"]) == b"AABB"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="No audio chunks"):
            AudioUtils.merge_and_encode([])


# ─── Voice Catalogue ─────────────────────────────────────────────────────────

class TestVoiceCatalogue:

    def test_all_voices_have_required_keys(self):
        required = {"label", "provider", "model", "gender", "style"}
        for vid, meta in VOICE_CATALOGUE.items():
            missing = required - meta.keys()
            assert not missing, f"Voice '{vid}' missing keys: {missing}"

    def test_indian_voices_have_instructions(self):
        for vid, meta in VOICE_CATALOGUE.items():
            if meta.get("indian"):
                assert meta.get("instructions"), \
                    f"Indian voice '{vid}' must have accent instructions"

    def test_indian_voices_use_mini_tts(self):
        """Accent-steering requires gpt-4o-mini-tts, not tts-1-hd."""
        for vid, meta in VOICE_CATALOGUE.items():
            if meta.get("indian"):
                assert meta["model"] == "gpt-4o-mini-tts", \
                    f"Indian voice '{vid}' should use gpt-4o-mini-tts"

    def test_expected_professional_male_voices(self):
        prof_male = [
            v for v, m in VOICE_CATALOGUE.items()
            if m["gender"] == "male" and m["style"] == "professional"
        ]
        assert len(prof_male) >= 2, "Need at least 2 professional male voices"

    def test_expected_indian_female_voices(self):
        indian_female = [
            v for v, m in VOICE_CATALOGUE.items()
            if m.get("indian") and m["gender"] == "female"
        ]
        assert len(indian_female) == 3, "Need exactly 3 Indian female voices"

    def test_voice_groups_reference_valid_ids(self):
        all_ids = set(VOICE_CATALOGUE.keys())
        for group_name, gdata in VOICE_GROUPS.items():
            for vid in gdata["voices"]:
                assert vid in all_ids, \
                    f"Group '{group_name}' references unknown voice '{vid}'"

    def test_provider_consistency(self):
        """Voice meta provider must match the model prefix."""
        for vid, meta in VOICE_CATALOGUE.items():
            if meta["provider"] == "Groq":
                assert "orpheus" in meta["model"] or "playai" in meta["model"].lower(), \
                    f"Groq voice '{vid}' has unexpected model '{meta['model']}'"
            elif meta["provider"] == "OpenAI":
                assert "tts" in meta["model"], \
                    f"OpenAI voice '{vid}' has unexpected model '{meta['model']}'"

"""
VoiceForge Text Processor
Cleans, analyses, and intelligently chunks text for TTS.
"""

import re
import math


class TextProcessor:
    """Pre-process raw input text for TTS synthesis."""

    # Average reading / speaking speed (words per minute)
    WPM = 150
    AVG_WORD_LEN = 5  # chars

    def __init__(self, text: str):
        self.raw = text

    # ─── Stats ───────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        text = self.raw.strip()
        chars = len(text)
        words = len(text.split()) if text else 0
        sentences = max(1, len(re.split(r'[.!?]+', text)))
        minutes = words / self.WPM
        if minutes < 1:
            duration = f"{int(minutes * 60)}s"
        elif minutes < 60:
            m = int(minutes)
            s = int((minutes - m) * 60)
            duration = f"{m}m {s}s"
        else:
            h = int(minutes // 60)
            m = int(minutes % 60)
            duration = f"{h}h {m}m"
        return {
            "chars": chars,
            "words": words,
            "sentences": sentences,
            "est_duration": duration,
        }

    # ─── Clean ───────────────────────────────────────────────────────────────────

    def clean(self) -> str:
        """
        Normalise text for TTS:
        - Collapse excessive whitespace / blank lines
        - Remove non-printable control chars
        - Normalise quotes & dashes
        """
        text = self.raw

        # Remove non-printable except newlines/tabs
        text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]', '', text)

        # Normalise curly quotes
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('\u201C', '"').replace('\u201D', '"')

        # Normalise dashes
        text = text.replace('\u2013', ' - ').replace('\u2014', ' — ')

        # Collapse 3+ blank lines → double newline
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Collapse multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    # ─── Chunk ───────────────────────────────────────────────────────────────────

    def chunk(self, max_chars: int = 4096) -> list[str]:
        """
        Split cleaned text into chunks ≤ max_chars, breaking only at
        sentence boundaries where possible, or word boundaries otherwise.
        """
        text = self.clean()
        if len(text) <= max_chars:
            return [text]

        chunks = []
        # Split into sentences
        sentence_pattern = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_pattern.split(text)

        current = ""
        for sentence in sentences:
            # If single sentence is too long, split by words
            if len(sentence) > max_chars:
                if current:
                    chunks.append(current.strip())
                    current = ""
                words = sentence.split()
                word_buf = ""
                for word in words:
                    if len(word_buf) + len(word) + 1 <= max_chars:
                        word_buf += (" " if word_buf else "") + word
                    else:
                        if word_buf:
                            chunks.append(word_buf.strip())
                        word_buf = word
                if word_buf:
                    current = word_buf
                continue

            candidate = (current + " " + sentence).strip() if current else sentence
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence

        if current:
            chunks.append(current.strip())

        return [c for c in chunks if c.strip()]

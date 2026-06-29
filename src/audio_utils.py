"""
VoiceForge Audio Utilities
Merges multi-chunk audio and re-encodes to 320kbps MP3 using pydub + ffmpeg.
Falls back to byte concatenation if ffmpeg is unavailable.
"""

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AudioUtils:

    @staticmethod
    def merge_and_encode(audio_chunks: list[bytes], bitrate: str = "320k") -> bytes:
        """
        Merge list of MP3 byte chunks into a single high-quality MP3.
        Uses pydub (ffmpeg) for proper merge + re-encode at target bitrate.
        Falls back to naive concatenation if ffmpeg is not installed.
        """
        if not audio_chunks:
            raise ValueError("No audio chunks to merge.")

        if len(audio_chunks) == 1 and bitrate == "320k":
            # Still re-encode single chunk to ensure 320kbps
            try:
                return AudioUtils._reencode(audio_chunks[0], bitrate)
            except Exception:
                return audio_chunks[0]

        try:
            from pydub import AudioSegment

            combined: Optional[AudioSegment] = None
            for chunk_bytes in audio_chunks:
                seg = AudioSegment.from_mp3(io.BytesIO(chunk_bytes))
                combined = seg if combined is None else combined + seg

            buf = io.BytesIO()
            combined.export(
                buf,
                format="mp3",
                bitrate=bitrate,
                parameters=["-q:a", "0"],  # highest quality VBR flag
            )
            buf.seek(0)
            return buf.read()

        except ImportError:
            logger.warning("pydub not available — falling back to byte concatenation.")
            return AudioUtils._concat_fallback(audio_chunks)
        except Exception as e:
            logger.warning(f"pydub merge failed ({e}) — falling back to byte concatenation.")
            return AudioUtils._concat_fallback(audio_chunks)

    @staticmethod
    def _reencode(audio_bytes: bytes, bitrate: str) -> bytes:
        from pydub import AudioSegment
        seg = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        buf = io.BytesIO()
        seg.export(buf, format="mp3", bitrate=bitrate, parameters=["-q:a", "0"])
        buf.seek(0)
        return buf.read()

    @staticmethod
    def _concat_fallback(chunks: list[bytes]) -> bytes:
        """Naive byte join — works for most players but may have gaps."""
        buf = io.BytesIO()
        for chunk in chunks:
            buf.write(chunk)
        buf.seek(0)
        return buf.read()

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024**2):.2f} MB"

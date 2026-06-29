"""
VoiceForge Analytics — session tracking and dashboard.
"""

import streamlit as st
from datetime import datetime


class Analytics:
    SK = "vf_analytics"

    def __init__(self):
        if self.SK not in st.session_state:
            st.session_state[self.SK] = {
                "total_conversions": 0,
                "total_chars": 0,
                "history": [],
                "provider_counts": {},
                "voice_counts": {},
                "indian_count": 0,
                "hourly_bins": {},
            }

    def _d(self) -> dict:
        return st.session_state[self.SK]

    def record_conversion(self, provider: str, voice_id: str, chars: int,
                          chunks: int, indian: bool = False):
        d = self._d()
        d["total_conversions"] += 1
        d["total_chars"]       += chars
        if indian:
            d["indian_count"] += 1
        hour = datetime.now().strftime("%H:00")
        d["hourly_bins"][hour]    = d["hourly_bins"].get(hour, 0) + 1
        d["provider_counts"][provider] = d["provider_counts"].get(provider, 0) + 1
        d["voice_counts"][voice_id]    = d["voice_counts"].get(voice_id, 0) + 1
        d["history"].append({
            "time":     datetime.now().strftime("%H:%M:%S"),
            "provider": provider,
            "voice":    voice_id,
            "chars":    chars,
            "chunks":   chunks,
            "indian":   "🇮🇳 Yes" if indian else "—",
        })

    def get_session_stats(self) -> dict:
        d = self._d()
        return {"total_conversions": d["total_conversions"], "total_chars": d["total_chars"]}

    def render_dashboard(self):
        import pandas as pd
        d = self._d()

        if d["total_conversions"] == 0:
            st.info("📊 No conversions yet. Generate audio to populate analytics.")
            self._render_voice_reference()
            return

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Conversions",        d["total_conversions"])
        k2.metric("Chars Processed",    f"{d['total_chars']:,}")
        k3.metric("Indian Accent Runs", d["indian_count"])
        k4.metric("Top Voice",          max(d["voice_counts"], key=d["voice_counts"].get, default="—"))

        st.markdown("---")
        ca, cb = st.columns(2)

        with ca:
            st.markdown("#### Provider Usage")
            if d["provider_counts"]:
                st.bar_chart(pd.DataFrame(list(d["provider_counts"].items()),
                                          columns=["Provider","Count"]).set_index("Provider"))

        with cb:
            st.markdown("#### Voice Usage")
            if d["voice_counts"]:
                df_v = (pd.DataFrame(list(d["voice_counts"].items()), columns=["Voice","Count"])
                          .sort_values("Count", ascending=False).set_index("Voice"))
                st.bar_chart(df_v)

        st.markdown("#### Hourly Activity")
        if d["hourly_bins"]:
            st.bar_chart(pd.DataFrame(sorted(d["hourly_bins"].items()),
                                       columns=["Hour","Count"]).set_index("Hour"))

        st.markdown("#### Conversion History")
        if d["history"]:
            df_h = pd.DataFrame(d["history"][::-1])
            df_h.columns = ["Time", "Provider", "Voice", "Characters", "Chunks", "Indian Accent"]
            st.dataframe(df_h, use_container_width=True, hide_index=True)

    def _render_voice_reference(self):
        from src.config import VOICE_GROUPS, VOICE_CATALOGUE
        st.markdown("---")
        st.markdown("#### Voice Reference")
        for group_name, gdata in VOICE_GROUPS.items():
            st.markdown(f"**{group_name}**")
            if "note" in gdata:
                st.caption(gdata["note"])
            for vid in gdata["voices"]:
                meta = VOICE_CATALOGUE[vid]
                indian_tag = " 🇮🇳" if meta.get("indian") else ""
                st.markdown(f"- `{vid}` · {meta['label']}{indian_tag} · `{meta['model']}`")
            st.markdown("")

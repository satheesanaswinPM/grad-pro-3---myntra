"""Run with: streamlit run mvp_app.py  (or: python -m streamlit run mvp_app.py)

Running `python -m src.mvp` directly (without streamlit) will not serve a UI -- Streamlit apps must
be launched through the streamlit CLI. This module exists so `python -m src.mvp` at least points you
at the right command instead of failing silently.
"""

from __future__ import annotations

if __name__ == "__main__":
    print("Run this app with:  streamlit run mvp_app.py")

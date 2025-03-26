import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import importlib.util

st.set_page_config(page_title="🕸️ Web Scraper Assistant", layout="wide")
st.title("🕸️ Modular Web Scraper Assistant (SPG v1)")

# Auto-load test config
default_config = {}
def_config_path = Path("config/test_web_scraper_config.json")
if def_config_path.exists():
    with open(def_config_path) as f:
        default_config = json.load(f)
        st.sidebar.success("✅ Test config loaded")

# Load scraper logic
scraper_path = Path("assistants/web_scraper.py")
if scraper_path.exists():
    spec = importlib.util.spec_from_file_location("web_scraper", scraper_path)
    web_scraper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web_scraper)
else:
    st.error("❌ assistants/web_scraper.py not found")
    st.stop()

# ----------- UI Controls (10+ Modular Sections) -----------
st.subheader("📋 Configuration")

url = st.text_input("🔗 Target URL", value=default_config.get("url", "https://books.toscrape.com/"))
prompt = st.text_input("🧠 Prompt Description", value=default_config.get("prompt", "Scrape books"))
filters = st.text_input("🔍 Filter Keywords (comma-separated)", value=default_config.get("filters", ""))
pages = st.slider("🧭 Pages to Crawl", 1, 10, value=default_config.get("pages", 1))
use_browser = st.checkbox("🧠 Use Headless Browser (JS Rendering)?", value=default_config.get("use_browser", False))
callback_url = st.text_input("📡 Webhook Callback URL", value=default_config.get("callback_url", ""))

# 🧪 Selector Upload
selectors_file = st.file_uploader("📂 Upload selectors.json", type=["json"])
selectors_path = default_config.get("selectors", "selectors.json")
if selectors_file:
    ts = datetime.now().strftime("%H%M%S")
    selectors_path = f"selectors_{ts}.json"
    with open(selectors_path, "wb") as f:
        f.write(selectors_file.read())
    st.success(f"✅ Uploaded {selectors_path}")

# 🏷️ Run Metadata Label
meta_note = st.text_input("📎 Optional Metadata Note", value="")

# 💾 Run Assistant
if st.button("🚀 Run Web Scraper"):
    config = {
        "task_type": "web_scraper",
        "url": url,
        "prompt": prompt,
        "filters": filters,
        "pages": pages,
        "use_browser": use_browser,
        "selectors": selectors_path,
        "callback_url": callback_url,
        "timestamp": datetime.now().isoformat(),
        "note": meta_note
    }
    result = web_scraper.run_web_scraper(config)
    st.subheader("📤 Assistant Output")
    st.json(result)

    if result.get("output") and os.path.exists(result["output"]):
        try:
            df = pd.read_csv(result["output"])
            st.dataframe(df.head())
        except Exception as e:
            st.warning(f"⚠️ Could not load CSV: {e}")


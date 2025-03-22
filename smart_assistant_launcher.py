import streamlit as st
import os
import json
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import zipfile

# 1️⃣ Fetch assistant metadata from backend
@st.cache_data
def fetch_assistant_list():
    try:
        res = requests.get("https://assistant-api-pzj8.onrender.com/assistants")
        return res.json().get("available", [])
    except:
        return []

# 2️⃣ Build assistant tag map (static for now)
ASSISTANT_TAGS = {
    "web_scraper": "🔎 Scraper",
    "api_fetcher": "🌐 API",
    "kep_extractor": "🧠 KEP",
    "blueprint_generator": "📐 Builder",
    "assistant_chainer": "🔁 Chainer"
}

st.set_page_config(layout="wide", page_title="🧠 Smart Assistant Launcher")
st.title("🧠 Smart Assistant Launcher")

# 10️⃣ Theme Switcher
st.sidebar.markdown("### ⚙️ Theme")
theme = st.sidebar.radio("Choose Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("<style>body{background-color:#1e1e1e;color:white;}</style>", unsafe_allow_html=True)

# Assistant picker
assistant_list = fetch_assistant_list()
selected = st.selectbox("Choose an Assistant", assistant_list)
tag = ASSISTANT_TAGS.get(selected, "🧠 General")
st.markdown(f"### {tag} Assistant: `{selected}`")

# 7️⃣ Visual Run Status Tracker (emoji placeholder)
status_emoji = "🟢" if selected else "🔴"
st.sidebar.markdown(f"#### Status: {status_emoji} Ready")

# 9️⃣ Assistant Creator UI (Upload to /assistants/)
st.sidebar.markdown("### 📥 Upload New Assistant")
upload = st.sidebar.file_uploader("Upload Assistant .py File", type="py")
if upload:
    Path("assistants").mkdir(exist_ok=True)
    target_path = Path("assistants") / upload.name
    with open(target_path, "wb") as f:
        f.write(upload.read())
    st.sidebar.success(f"Uploaded {upload.name} ✅")

# 2️⃣ Per-Assistant Input Forms
with st.form("assistant_form"):
    prompt = st.text_input("Prompt")
    url = st.text_input("URL", "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd")
    filters = st.text_input("Filters (comma-separated)", "price, rating")
    submitted = st.form_submit_button("💾 Submit & Trigger")

    if submitted:
        config = {
            "task_type": selected,
            "prompt": prompt,
            "url": url,
            "filters": filters,
            "timestamp": datetime.now().isoformat()
        }
        filename = f"config_{selected}_{uuid4().hex[:6]}.json"
        with open(os.path.join("config", filename), "w") as f:
            json.dump(config, f, indent=2)

        # 3️⃣ Live Webhook Logs
        with st.spinner("🚀 Running assistant via webhook..."):
            try:
                res = requests.post("https://assistant-api-pzj8.onrender.com/run-assistant", json=config)
                if res.status_code == 200:
                    result = res.json()
                    st.success("✅ Assistant completed!")
                    st.code(json.dumps(result, indent=2), language="json")
                else:
                    st.error(f"❌ Webhook failed: {res.status_code}")
            except Exception as e:
                st.error(f"❌ Request error: {e}")

# 5️⃣ Config Browser
st.sidebar.markdown("### 📂 Browse Config Files")
config_dir = Path("config")
config_dir.mkdir(exist_ok=True)
all_configs = sorted(config_dir.glob("*.json"), reverse=True)[:5]
for cfile in all_configs:
    with st.sidebar.expander(f"🧾 {cfile.name}"):
        with open(cfile) as f:
            st.json(json.load(f))

# 6️⃣ Output ZIP Downloader + Run Replayer
st.sidebar.markdown("### 🗂 Run Archives")
output_dir = Path("output")
archive_dir = Path("archive")
archive_dir.mkdir(exist_ok=True)

for assistant in sorted(output_dir.iterdir()):
    if assistant.is_dir():
        latest_zip = archive_dir / f"{assistant.name}_latest.zip"
        zipf = zipfile.ZipFile(latest_zip, 'w')
        files = list(assistant.glob("*"))
        for f in files:
            zipf.write(f, arcname=f.name)
        zipf.close()
        with st.sidebar.expander(f"📦 {assistant.name}"):
            st.download_button("⬇️ Download Archive", latest_zip.read_bytes(), file_name=latest_zip.name)
            for f in files[:3]:
                st.caption(f.name)

# 8️⃣ Assistant Tags Display
st.sidebar.markdown("### 🏷 Assistant Tags")
for name, tag in ASSISTANT_TAGS.items():
    st.sidebar.markdown(f"- `{name}` → {tag}")


# Constants
API_BASE = "https://assistant-api-pzj8.onrender.com"

# Cached assistant description
@st.cache_data
def get_assistant_description(task):
    try:
        res = requests.get(f"{API_BASE}/docs/{task}")
        return res.text if res.status_code == 200 else None
    except:
        return None

# 11️⃣ Assistant Description Block (refined)
st.sidebar.markdown("### 📘 Assistant Description")
description = get_assistant_description(selected)
if description:
    st.sidebar.markdown(description)
else:
    st.sidebar.info("ℹ️ Description unavailable for this assistant.")

# 12️⃣ Recently Used Assistant Tracker (refined)
recent_path = Path("recent.json")
if recent_path.exists():
    with open(recent_path) as f:
        recent = json.load(f)
else:
    recent = []
if selected:
    if selected in recent:
        recent.remove(selected)
    recent.insert(0, selected)
    recent = recent[:5]
    with open(recent_path, "w") as f:
        json.dump(recent, f)
if recent:
    st.sidebar.markdown("### ⏱ Recently Used")
    for r in recent:
        st.sidebar.markdown(f"- `{r}`")

# 13️⃣ Save Result Metadata After Run (refined)
runlog_path = Path("logs/run_summary.jsonl")
runlog_path.parent.mkdir(parents=True, exist_ok=True)
if submitted:
    try:
        with open(runlog_path, "a") as log:
            log.write(json.dumps({
                "task_type": selected,
                "timestamp": config.get("timestamp", datetime.now().isoformat()),
                "filename": filename
            }) + "\n")
    except Exception as e:
        st.warning(f"⚠️ Failed to log run summary: {e}")

# 14️⃣ Display Last Run Summary (refined)
st.sidebar.markdown("### 🧾 Last Run Summary")
try:
    with open(runlog_path) as f:
        lines = f.readlines()
        if lines:
            last = json.loads(lines[-1])
            st.sidebar.success(f"✅ `{last['task_type']}` at `{last['timestamp']}`")
except Exception as e:
    st.sidebar.warning("⚠️ Last run summary corrupted.")

# 15️⃣ Docs & Guide Link (refined)
st.sidebar.markdown("---")
st.sidebar.markdown("[📘 Docs & Guide](https://github.com/MeatheadsMarketing/assistant_api)")
st.sidebar.caption("Build v1.0 • GitHub synced")

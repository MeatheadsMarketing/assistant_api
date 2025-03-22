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


# 16️⃣ Run Metrics Tracker (enhanced with size check)
st.sidebar.markdown("### 📊 Run Metrics")
log_file = "logs/run_summary.jsonl"
try:
    if os.path.exists(log_file) and os.path.getsize(log_file) < 1_000_000:
        summary_df = pd.read_json(log_file, lines=True)
        counts = summary_df["task_type"].value_counts().to_dict()
        for name, count in counts.items():
            st.sidebar.markdown(f"`{name}` → {count} runs")
    else:
        st.sidebar.caption("⚠️ Log too large or unavailable.")
except Exception as e:
    st.sidebar.caption(f"⚠️ Failed to load metrics: {e}")

# 17️⃣ Config Comparison Tool (with full views)
st.sidebar.markdown("### 🔍 Compare Configs")
if len(all_configs) >= 2:
    config_a = st.sidebar.selectbox("Config A", all_configs, index=0)
    config_b = st.sidebar.selectbox("Config B", all_configs, index=1)
    if st.sidebar.button("🧬 Compare JSONs"):
        with open(config_a) as a, open(config_b) as b:
            json_a = json.load(a)
            json_b = json.load(b)
        st.markdown("#### 🔍 JSON A vs JSON B")
        st.json({"A Only": {k: v for k, v in json_a.items() if k not in json_b},
                 "B Only": {k: v for k, v in json_b.items() if k not in json_a}})
        with st.expander("Full Config A"):
            st.json(json_a)
        with st.expander("Full Config B"):
            st.json(json_b)

# 18️⃣ Assistant Category Filter (static for now)
st.sidebar.markdown("### 🎛 Filter by Category")
categories = {
    "🧠 NLP": ["gpt_kep", "clarity_summarizer"],
    "🔁 Utility": ["api_fetcher", "web_scraper"]
}
selected_cat = st.sidebar.radio("Filter Assistants", list(categories.keys()) + ["All"])
if selected_cat != "All":
    assistant_list = [a for a in assistant_list if a in categories[selected_cat]]

# 19️⃣ Versioned Config Saving (refined path)
if submitted:
    version = datetime.now().strftime("v%Y%m%d_%H%M%S")
    versioned_name = f"config_{selected}_{version}.json"
    config_path = Path("config") / selected
    config_path.mkdir(parents=True, exist_ok=True)
    with open(config_path / versioned_name, "w") as f:
        json.dump(config, f, indent=2)
    st.sidebar.success(f"✅ Saved versioned config: {versioned_name}")

# 20️⃣ Auto-Replay Config with banner
st.sidebar.markdown("### 🔁 Replay Last Config")
if all_configs:
    replay = st.sidebar.selectbox("Choose config to replay", all_configs)
    if st.sidebar.button("🚀 Re-run Config"):
        with open(replay) as f:
            replay_config = json.load(f)
        try:
            res = requests.post("https://assistant-api-pzj8.onrender.com/run-assistant", json=replay_config)
            if res.status_code == 200:
                result = res.json()
                st.success("✅ Replayed config successfully!")
                st.code(json.dumps(result, indent=2), language="json")
                st.sidebar.success(f"✅ Replayed `{replay_config['task_type']}` config")
            else:
                st.error(f"❌ Replay failed: {res.status_code}")
        except Exception as e:
            st.error(f"❌ Replay error: {e}")



# 21️⃣ Display config path with validation
if submitted:
    full_path = config_path / versioned_name
    if os.path.exists(full_path):
        st.sidebar.markdown(f"🧭 Config Path: `{full_path}`")
    else:
        st.sidebar.warning("⚠️ Config path may not be accessible.")

# 22️⃣ Assistant Registry Ping with Timestamp
try:
    st.sidebar.markdown("### 📘 Registry Status")
    ping = requests.get("https://assistant-api-pzj8.onrender.com/assistants").json()
    st.sidebar.success("✅ Registered: " + ", ".join(ping.get("available", [])))
    st.sidebar.caption(f"Last check: {datetime.now().strftime('%H:%M:%S')}")
except:
    st.sidebar.warning("⚠️ Assistant registry could not be loaded.")

# 23️⃣ Run Summary Chart (with robustness)
try:
    history_df = pd.read_json("logs/run_summary.jsonl", lines=True)
    success_counts = history_df["task_type"].value_counts().reset_index()
    success_counts.columns = ["task", "runs"]
    st.sidebar.markdown("### 📈 Run Summary Chart")
    st.sidebar.bar_chart(success_counts.set_index("task"))
except Exception as e:
    st.sidebar.caption(f"⚠️ Not enough data for chart. ({e})")

# 24️⃣ Most Common Filters (normalized)
try:
    filters_cleaned = history_df["filters"].dropna().str.strip().str.lower()
    most_used_filters = filters_cleaned.value_counts().head(5)
    st.sidebar.markdown("### 🔍 Top Filters")
    for k, v in most_used_filters.items():
        st.sidebar.markdown(f"- `{k}` ×{v}")
except:
    st.sidebar.caption("⚠️ No filter stats yet.")

# 25️⃣ Export Full Log File + Log Tail Preview
log_file_path = "logs/run_summary.jsonl"
if os.path.exists(log_file_path):
    st.sidebar.download_button(
        label="⬇️ Export Run Log",
        data=open(log_file_path, "rb"),
        file_name="run_summary.jsonl",
        mime="text/plain"
    )
    try:
        with open(log_file_path) as f:
            tail = list(f.readlines())[-5:]
            with st.sidebar.expander("📄 Preview Last 5 Log Entries"):
                for line in tail:
                    st.code(line.strip())
    except:
        st.sidebar.caption("⚠️ Failed to preview tail of log.")



# 26️⃣ Assistant Type Quick Switcher (improved rerun logic)
st.sidebar.markdown("### 🔁 Quick Switch")
quick_switch = st.sidebar.selectbox("Jump to Assistant", assistant_list, index=0)
if quick_switch != selected and "switch_target" not in st.session_state:
    st.session_state["switch_target"] = quick_switch
    st.experimental_rerun()

# 27️⃣ Filter Assistant Dropdown by Keyword (refined)
st.sidebar.markdown("### 🔎 Search Assistants")
search = st.sidebar.text_input("Type to filter", "")
if search:
    assistant_list = [a for a in assistant_list if search.lower().strip() in a.lower()]

# 28️⃣ Output File Explorer (with size and modified time)
st.sidebar.markdown("### 📂 Output File Explorer")
if output_dir.exists():
    assistant_folders = [f for f in output_dir.iterdir() if f.is_dir()]
    for folder in assistant_folders:
        with st.sidebar.expander(f"📁 {folder.name}"):
            files = list(folder.glob("*"))
            for file in files[:3]:
                size = file.stat().st_size
                mod_time = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(f"- `{file.name}` • {size} bytes • {mod_time}")

# 29️⃣ Toggle Display Mode (refined with session)
display_mode = st.sidebar.radio("Display Mode", ["Compact", "Full"])
st.sidebar.markdown(f"🧰 Current Mode: `{display_mode}`")
if display_mode == "Compact":
    st.markdown("<style>div.block-container{padding:1rem;}</style>", unsafe_allow_html=True)

# 30️⃣ Visual Assistant Icon Map (ready for interactive expansion)
st.sidebar.markdown("### 🧩 Assistant Icons")
for k, v in ASSISTANT_TAGS.items():
    icon = v.split()[0]
    st.sidebar.markdown(f"- {icon} `{k}`")


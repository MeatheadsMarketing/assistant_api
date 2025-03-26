import streamlit as st
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

from backend_api.runner import run_assistant

CONFIG_DIR = "config"
OUTPUT_DIR = "output"
Path(CONFIG_DIR).mkdir(exist_ok=True)
Path(OUTPUT_DIR).mkdir(exist_ok=True)

st.set_page_config(layout="wide", page_title="🧠 API Fetcher Assistant (SPG v1)")
st.title("🧠 Modular API Fetcher Assistant (SPG v1)")
st.subheader("⚙️ Configuration")

# Auto-load test config if found
def load_test_config():
    test_path = Path(CONFIG_DIR) / "test_api_fetcher_config.json"
    if test_path.exists():
        with open(test_path) as f:
            return json.load(f)
    return {}

state = load_test_config()

# --- Modular Dropdowns ---
api_url = st.text_input("🔗 API Endpoint", state.get("url", "https://api.example.com/data"))
headers_input = st.text_area("🧾 Custom Headers (JSON)", value=state.get("headers", ""))
query_params = st.text_area("🔍 Query Parameters (JSON)", value=state.get("params", ""))
auth_token = st.text_input("🔐 Bearer Token", state.get("auth_token", ""))
retry_count = st.slider("🔁 Retry Attempts", 0, 5, value=state.get("retries", 2))
timeout = st.slider("⏱️ Timeout (secs)", 1, 60, value=state.get("timeout", 10))
fetch_mode = st.selectbox("📦 Response Mode", ["json", "text", "binary"], index=0)
run_metadata = st.text_input("🧠 Metadata Tag", state.get("metadata", "testing-api"))

# --- Trigger Button ---
if st.button("🚀 Run API Fetcher"):
    config = {
        "task_type": "api_fetcher",
        "url": api_url,
        "headers": headers_input,
        "params": query_params,
        "auth_token": auth_token,
        "retries": retry_count,
        "timeout": timeout,
        "mode": fetch_mode,
        "metadata": run_metadata,
        "timestamp": datetime.now().isoformat()
    }
    
    run_id = f"api_fetcher_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    config_path = Path(CONFIG_DIR) / run_id
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    
    st.success(f"✅ Config saved to {config_path.name}")

    # Call backend
    result = run_assistant(config)
    st.subheader("📤 API Result")
    st.write(result)

# --- Config Loader Sidebar ---
st.sidebar.markdown("### 📂 Load Test Config")
st.sidebar.info("Test config will load defaults into dropdowns on page load")

# --- Output Archive & Export Stub ---
st.markdown("---")
st.subheader("📦 Output Archive for API Fetcher")
st.write("(Auto-archive + zip download planned)")

import streamlit as st
st.set_page_config(layout="wide", page_title="🧠 Smart Assistant Launcher")

import os
import json
import uuid
from datetime import datetime
import requests  # ✅ Added this import

from pathlib import Path
from runner import run_assistant

# Sidebar - Upload section
st.sidebar.header("📂 Upload Google Credentials")
client_secret = st.sidebar.file_uploader("Upload your Google Drive service account JSON", type="json")
if client_secret:
    with open("client_secret.json", "wb") as f:
        f.write(client_secret.read())
    st.sidebar.success("✅ Credentials file saved")

# Load available assistants
ASSISTANT_FOLDER = "assistants"
available_assistants = [f.replace(".py", "") for f in os.listdir(ASSISTANT_FOLDER) if f.endswith(".py")]

# Select assistant from dropdown
st.header("🧠 Smart Assistant Launcher")
st.subheader("⚙️ Choose Assistant")
selected_assistant = st.selectbox("Available Assistants", available_assistants)
st.session_state["selected_assistant"] = selected_assistant

# Prompt block
prompt = st.text_input("🧠 Prompt", placeholder="Describe what the assistant should do...")

# URL
url = st.text_input("🔗 Target URL", placeholder="https://example.com")

# Filters
filters = st.text_input("🧹 Filters (comma-separated)", placeholder="price, rating")

# Run button
if st.button("🚀 Save & Run Assistant"):
    config = {
        "task_type": selected_assistant,
        "prompt": prompt,
        "url": url,
        "filters": filters,
        "timestamp": datetime.now().isoformat()
    }

    # Save config locally
    config_name = f"assistant_config_{selected_assistant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("config", exist_ok=True)
    with open(os.path.join("config", config_name), "w") as f:
        json.dump(config, f, indent=4)

    # Try to run assistant
    try:
        result = run_assistant(config)
        st.success("✅ Assistant triggered successfully!")
        st.json(result)
    except Exception as e:
        st.error(f"❌ Failed to reach assistant API: {e}")

# Preview latest CSV from output
st.markdown("### 📄 Latest Output Preview")
OUTPUT_DIR = "output"
latest_file = ""
output_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")])
if output_files:
    latest_file = output_files[-1]
    st.markdown(f"📎 Showing latest output file: `{latest_file}`")
    try:
        import pandas as pd
        df = pd.read_csv(os.path.join(OUTPUT_DIR, latest_file))
        st.dataframe(df)
    except Exception as e:
        st.warning(f"{latest_file} is empty or malformed – no preview available.")
else:
    st.info("No CSV outputs available yet.")

# Validate assistant for output archive and run log
if "selected_assistant" in st.session_state:
    selected_assistant = st.session_state["selected_assistant"]
else:
    selected_assistant = ""

if selected_assistant and output_files:
    st.markdown("### 📦 Output Archive for Selected Assistant")
    st.info(f"No outputs found yet for assistant `{selected_assistant}`.")

    st.markdown("### 🧠 Run History & Bundled Exports")
    st.info("No run history available yet.") 


import streamlit as st
import os
import pandas as pd
import json

OUTPUT_DIR = "output"

st.set_page_config(page_title="Assistant Preview", layout="wide")
st.title("📁 Assistant Output Archive & Run History")

# Get available assistants from output folders
assistants = sorted([d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))])
selected = st.sidebar.selectbox("🧠 Choose Assistant", assistants)

if selected:
    output_path = os.path.join(OUTPUT_DIR, selected)
    history_path = os.path.join(output_path, "history.json")

    st.subheader(f"📜 Run History for `{selected}`")
    if os.path.exists(history_path):
        with open(history_path) as f:
            history = json.load(f)

        for run in reversed(history[-5:]):  # show last 5 runs
            st.markdown(f"**🕒 {run['timestamp']}** — `{run.get('prompt', '')}`")
            if run.get("file", "").endswith(".csv"):
                try:
                    df = pd.read_csv(os.path.join(output_path, run["file"]))
                    st.dataframe(df)
                except:
                    st.warning(f"{run['file']} is empty or malformed.")
            elif run.get("file", "").endswith(".json"):
                try:
                    with open(os.path.join(output_path, run["file"])) as j:
                        data = json.load(j)
                        st.json(data)
                except:
                    st.warning(f"{run['file']} is malformed.")
    else:
        st.info("No run history found for this assistant.")

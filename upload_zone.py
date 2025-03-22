# 📦 Upload Zone UI Component for Smart Assistant Launcher

import streamlit as st
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

st.sidebar.markdown("### 🔼 Upload Assistant Script (.py)")
assistant_file = st.sidebar.file_uploader("Upload .py file", type=["py"], key="upload_py")

if assistant_file:
    filename = UPLOAD_DIR / assistant_file.name
    with open(filename, "wb") as f:
        f.write(assistant_file.read())
    st.sidebar.success(f"✅ Uploaded: {filename.name}")

st.sidebar.markdown("---")

st.sidebar.markdown("### 🔐 Upload Config or Secret File (.json)")
json_file = st.sidebar.file_uploader("Upload .json file", type=["json"], key="upload_json")

if json_file:
    filename = UPLOAD_DIR / json_file.name
    with open(filename, "wb") as f:
        f.write(json_file.read())
    st.sidebar.success(f"✅ Uploaded: {filename.name}")

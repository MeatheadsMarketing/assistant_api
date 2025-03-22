import streamlit as st
from pathlib import Path

# Directories for uploads
ASSISTANT_DIR = Path("assistants")
SECRET_DIR = Path("secrets")
ASSISTANT_DIR.mkdir(exist_ok=True)
SECRET_DIR.mkdir(exist_ok=True)
# Ensure assistants is a package for import
init_file = ASSISTANT_DIR / "__init__.py"
if not init_file.exists():
    init_file.write_text("")

st.sidebar.markdown("### 🔼 Upload Assistant Script (.py)")
assistant_file = st.sidebar.file_uploader("Upload a new assistant (.py)", type="py", key="upload_py")
if assistant_file:
    file_path = ASSISTANT_DIR / assistant_file.name
    file_bytes = assistant_file.read()
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    st.sidebar.success(f"✅ Uploaded assistant: {assistant_file.name}")

st.sidebar.markdown("### 🔐 Upload Config/Secret (.json)")
json_file = st.sidebar.file_uploader("Upload config or credentials (.json)", type="json", key="upload_json")
if json_file:
    file_path = SECRET_DIR / json_file.name
    with open(file_path, "wb") as f:
        f.write(json_file.read())
    st.sidebar.success(f"✅ Uploaded file: {json_file.name}")

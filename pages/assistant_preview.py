import streamlit as st
import os
import yaml
import pandas as pd

OUTPUTS_DIR = "outputs"

st.set_page_config(page_title="Assistant Preview", layout="wide")
st.title("🧠 Assistant Preview")

# 🔍 Scan assistant folders

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
assistants = sorted(os.listdir(OUTPUT_DIR))

selected_assistant = st.selectbox("Choose Assistant:", assistants)

assistant_path = os.path.join(OUTPUTS_DIR, selected_assistant)
files = os.listdir(assistant_path)

# 🔍 Load YAML
yaml_file = next((f for f in files if f.endswith("_blueprint") and f.endswith(".yaml")), None)
if yaml_file:
    with open(os.path.join(assistant_path, yaml_file), "r", encoding="utf-8") as f:
        blueprint_data = yaml.safe_load(f)
    st.subheader("📘 Assistant Blueprint (YAML)")
    st.code(yaml.dump(blueprint_data, sort_keys=False), language="yaml")

# 📝 Load Markdown
md_file = next((f for f in files if f.endswith("_card") and f.endswith(".md")), None)
if md_file:
    with open(os.path.join(assistant_path, md_file), "r", encoding="utf-8") as f:
        markdown_content = f.read()
    st.subheader("🧾 Assistant Card (Markdown)")
    st.markdown(markdown_content)

# 📊 Load CSV
csv_file = next((f for f in files if f.endswith("_kep") and f.endswith(".csv")), None)
if csv_file:
    df = pd.read_csv(os.path.join(assistant_path, csv_file))
    st.subheader("📊 Assistant Concepts (KEP CSV)")
    st.dataframe(df)

# 📥 Download All
st.markdown("---")
st.subheader("⬇️ Download Files")
for f in files:
    with open(os.path.join(assistant_path, f), "rb") as file:
        st.download_button(label=f"Download {f}", data=file, file_name=f)

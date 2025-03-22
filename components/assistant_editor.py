# components/assistant_editor.py

import os
import yaml
import json
import streamlit as st
from datetime import datetime

def render_assistant_editor(assistant_path: str):
    st.markdown("## ✏️ Assistant Config Editor & Launcher")

    # --- Detect files ---
    yaml_file = next((f for f in os.listdir(assistant_path) if f.endswith("_blueprint") and f.endswith(".yaml")), None)
    json_file = next((f for f in os.listdir(assistant_path) if f.endswith("_summary") and f.endswith(".json")), None)

    # --- Load YAML ---
    blueprint_data = {}
    if yaml_file:
        with open(os.path.join(assistant_path, yaml_file), "r") as f:
            blueprint_data = yaml.safe_load(f)
        st.markdown("### 🧠 Blueprint Logic")
        with st.expander("🔍 View YAML Blueprint"):
            st.code(yaml.dump(blueprint_data, sort_keys=False), language="yaml")

    # --- Load JSON Summary ---
    summary_data = {}
    if json_file:
        with open(os.path.join(assistant_path, json_file), "r") as f:
            summary_data = json.load(f)

    # --- Editable Config Form ---
    st.markdown("### 🛠️ Edit Assistant Config")
    editable_config = {}
    with st.form("edit_form"):
        for key, value in blueprint_data.items():
            if isinstance(value, str):
                editable_config[key] = st.text_input(f"{key}", value)
            elif isinstance(value, list):
                joined = ", ".join(value)
                editable_config[key] = st.text_area(f"{key}", joined).split(",")
            elif isinstance(value, dict):
                editable_config[key] = value  # Nested dict (like logic_blocks) shown only in YAML preview

        launch = st.form_submit_button("🚀 Launch Assistant")

    # --- Handle Launch Logic ---
    if launch:
        st.markdown("#### ⏳ Running Assistant...")
        try:
            # Insert your assistant runner logic here
            st.success("✅ Assistant Launched!")
            st.json(editable_config)
        except Exception as e:
            st.error(f"❌ Launch Failed: {e}")

    # --- Quick Clone Button ---
    if st.button("🔁 Quick Clone Assistant"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clone_name = editable_config.get("assistant_name", "assistant_clone") + f"_clone_{timestamp}"
        clone_path = os.path.join("outputs", clone_name)
        os.makedirs(clone_path, exist_ok=True)

        # Clone files
        for file in os.listdir(assistant_path):
            original = os.path.join(assistant_path, file)
            if os.path.isfile(original):
                target = os.path.join(clone_path, file.replace(editable_config.get("assistant_name", ""), clone_name))
                with open(original, "r", encoding="utf-8") as f_in, open(target, "w", encoding="utf-8") as f_out:
                    content = f_in.read().replace(editable_config.get("assistant_name", ""), clone_name)
                    f_out.write(content)

        st.success(f"✅ Assistant cloned to: `{clone_name}`")

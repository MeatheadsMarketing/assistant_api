import streamlit as st
import os, json
import pandas as pd

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.title("📁 Assistant Output Archive")
# List available assistants (output subdirectories)
assistants = sorted([name for name in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, name))])
selected = st.selectbox("Choose an assistant", ["(select)"] + assistants, index=0)
if selected and selected != "(select)":
    st.markdown(f"## Outputs for `{selected}`")
    files = sorted(os.listdir(os.path.join(OUTPUT_DIR, selected)), reverse=True)
    if not files:
        st.info("No output files available yet for this assistant.")
    for fname in files:
        file_path = os.path.join(OUTPUT_DIR, selected, fname)
        st.markdown(f"**{fname}**")
        if fname.endswith(".csv"):
            try:
                df = pd.read_csv(file_path)
                st.dataframe(df)
            except Exception as e:
                st.warning(f"⚠️ Could not read `{fname}`: {e}")
        elif fname.endswith((".yaml", ".yml")):
            try:
                text = open(file_path, "r").read()
                st.code(text, language="yaml")
            except Exception as e:
                st.warning(f"⚠️ Could not read `{fname}`: {e}")
        elif fname.endswith(".md"):
            try:
                text = open(file_path, "r").read()
                st.markdown(text)
            except Exception as e:
                st.warning(f"⚠️ Could not read `{fname}`: {e}")
        else:
            # Generic file handling
            st.text(f"Stored at: {file_path}")
        # Provide a download button for each file
        try:
            with open(file_path, "rb") as f:
                st.download_button(f"⬇️ Download {fname}", f.read(), file_name=fname)
        except Exception as e:
            st.write(f"*Could not prepare download: {e}*")

# 📁 Output File Export UI (Downloads, ZIPs, Archive Buttons)
import streamlit as st
import zipfile
from pathlib import Path
import shutil

EXPORT_DIR = Path("output")
ARCHIVE_DIR = Path("archive")
ARCHIVE_DIR.mkdir(exist_ok=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📤 Export Output Files")

# 🔽 Select assistant folder to browse
assistant_dirs = [d for d in EXPORT_DIR.iterdir() if d.is_dir()]
selected_assistant = st.sidebar.selectbox("Choose assistant output folder", [d.name for d in assistant_dirs])

output_files = list((EXPORT_DIR / selected_assistant).glob("*.csv"))

if output_files:
    with st.sidebar.expander("📦 Download Individual Files"):
        for f in output_files:
            with open(f, "rb") as file_data:
                st.download_button(f"⬇️ {f.name}", file_data.read(), file_name=f.name)

    with st.sidebar.expander("🗜 Create ZIP Archive"):
        zip_path = ARCHIVE_DIR / f"{selected_assistant}_export.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for f in output_files:
                zipf.write(f, arcname=f.name)
        with open(zip_path, "rb") as zf:
            st.download_button("📁 Download ZIP", zf.read(), file_name=zip_path.name)
else:
    st.sidebar.warning("⚠️ No .csv files found in this assistant folder.")

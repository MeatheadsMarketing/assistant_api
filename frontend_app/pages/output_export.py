import streamlit as st
import zipfile
from pathlib import Path

EXPORT_DIR = Path("output")
ARCHIVE_DIR = Path("archive")
ARCHIVE_DIR.mkdir(exist_ok=True)

st.sidebar.markdown("### 📤 Export Output Files")
# List available assistant output folders
assistant_dirs = [d for d in EXPORT_DIR.iterdir() if d.is_dir()]
if not assistant_dirs:
    st.sidebar.info("No outputs available to export yet.")
else:
    selected_assistant = st.sidebar.selectbox(
        "Choose assistant output folder", [d.name for d in assistant_dirs]
    )
    output_files = list((EXPORT_DIR / selected_assistant).glob("*.csv"))
    if output_files:
        with st.sidebar.expander("📑 Download Individual CSVs"):
            for f_path in output_files:
                with open(f_path, "rb") as f:
                    st.download_button(f"⬇️ {f_path.name}", f.read(), file_name=f_path.name)
        with st.sidebar.expander("🗜 Download All as ZIP"):
            zip_path = ARCHIVE_DIR / f"{selected_assistant}_export.zip"
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for f_path in output_files:
                    zipf.write(f_path, arcname=f_path.name)
            with open(zip_path, "rb") as zf:
                st.download_button("⬇️ Download ZIP archive", zf.read(), file_name=zip_path.name)
    else:
        st.sidebar.warning(f"⚠️ No CSV files found in `{selected_assistant}` outputs.")

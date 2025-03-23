import pandas as pd
from datetime import datetime
import streamlit as st
st.set_page_config(page_title="🧠 Smart Assistant Launcher", layout="wide")  # ← Move this here

from datetime import datetime
from pathlib import Path
import json, os, uuid
from frontend_app.pages import upload_zone
from frontend_app.pages import output_export



st.title("🧠 Smart Assistant Launcher")

# ✅ Sidebar: Google Drive Credentials upload
st.sidebar.subheader("🔐 Upload Google Credentials")
creds_file = st.sidebar.file_uploader("Upload your Google Drive service account JSON", type="json")
if creds_file:
    with open("client_secret.json", "wb") as f:
        f.write(creds_file.read())
    st.sidebar.success("✅ Credentials file saved")

# ✅ Google Drive upload helper
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path, file_name):
    """Upload a file to Google Drive (root directory) using service account credentials."""
    creds = service_account.Credentials.from_service_account_file(
        "client_secret.json", scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": file_name, "parents": ["root"]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/file/d/{uploaded['id']}/view"

# ✅ Load available assistants dynamically
ASSISTANT_DIR = "assistants"
os.makedirs(ASSISTANT_DIR, exist_ok=True)
# Ensure assistants folder is a package for dynamic import
init_file = os.path.join(ASSISTANT_DIR, "__init__.py")
if not os.path.exists(init_file):
    open(init_file, "a").close()
try:
    assistant_types = sorted([
        f.replace(".py", "") for f in os.listdir(ASSISTANT_DIR)
        if f.endswith(".py") and not f.startswith("__")
    ])
except Exception as e:
    assistant_types = []
    st.sidebar.warning(f"⚠️ Error loading assistants: {e}")

# ✅ Assistant selection
st.markdown("## ⚙️ Choose Assistant")
if assistant_types:
    task_type = st.selectbox("Available Assistants", assistant_types)
else:
    task_type = None
    st.warning("⚠️ No assistant scripts found. Upload a .py file to get started.")

# ✅ Assistant configuration form
with st.form("assistant_form"):
    prompt = st.text_input("Prompt", "Scrape latest laptops from Newegg with prices and ratings")
    url = st.text_input("Target URL", "https://www.newegg.com/laptops")
    filters = st.text_input("Filters (comma-separated)", "price, rating")

    # Show additional input fields for specific assistant types
    if task_type == "kep_extractor":
        st.header("📘 KEP Extractor Inputs")
        course_title = st.text_input("Course Title")
        module_title = st.text_input("Module Title")
        lesson_input = st.text_area("Lesson Titles (comma-separated)")
        lesson_titles = [l.strip() for l in lesson_input.split(",") if l.strip()]
    elif task_type == "blueprint_generator":
        st.header("📐 Blueprint Generator Inputs")
        uploaded_csv = st.file_uploader("Upload KEP CSV", type="csv")

    submitted = st.form_submit_button("💾 Save & Run Assistant")

# ✅ Handle form submission
if submitted and task_type:
    # Build config data for the assistant
    config_data = {
        "task_type": task_type,
        "prompt": prompt,
        "url": url,
        "filters": filters,
        "timestamp": datetime.now().isoformat()
    }
    # Include additional fields for specific tasks
    if task_type == "kep_extractor":
        config_data.update({
            "course_title": course_title,
            "module_title": module_title,
            "lesson_titles": lesson_titles
        })
    elif task_type == "blueprint_generator" and uploaded_csv is not None:
        csv_path = f"uploaded_kep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_path, "wb") as f:
            f.write(uploaded_csv.read())
        config_data["uploaded_kep_csv"] = csv_path

    # Save config to JSON file and upload to Drive
    config_filename = f"assistant_config_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(config_filename, "w") as f:
        json.dump(config_data, f, indent=4)
    try:
        drive_link = upload_to_drive(config_filename, config_filename)
        st.success("✅ Configuration saved to Google Drive")
        st.markdown(f"[📄 View config on Drive]({drive_link})")
    except Exception as e:
        st.error(f"❌ Drive upload failed: {e}")

    # Trigger backend API to run the assistant
    api_base = os.getenv("ASSISTANT_API_URL", "https://assistant-api-pzj8.onrender.com")
    api_url = f"{api_base}/run-assistant"
    try:
        res = requests.post(api_url, json=config_data, timeout=30)
    except Exception as e:
        res = None
        st.error(f"❌ Failed to reach assistant API: {e}")
    if res and res.status_code == 200:
        result = res.json()
        st.success("📬 Assistant triggered successfully!")
        st.json(result)  # Display JSON response (status and any outputs)
    else:
        if res:
            st.error(f"❌ Assistant API error (status {res.status_code})")
            st.write(res.text)
        # If no response at all (exception above), error is already shown.

    # Record last run status in session for sidebar diagnostics
    st.session_state.last_run = {
        "assistant": task_type,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status_code": res.status_code if res else None,
        "result_json": (res.json() if res and res.headers.get("content-type","").startswith("application/json") else None)
    }

# ✅ Latest output preview (quick view for convenience)
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
st.markdown("---")
st.subheader("📄 Latest Output Preview")
csv_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")]
if csv_files:
    latest_file = sorted(csv_files, reverse=True)[0]
    st.markdown(f"📁 Showing latest output file: `{latest_file}`")
    try:
        df = pd.read_csv(os.path.join(OUTPUT_DIR, latest_file))
        st.dataframe(df.head(10))
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=latest_file)
    except pd.errors.EmptyDataError:
        st.warning(f"⚠️ `{latest_file}` is empty or malformed – no preview available.")
    except Exception as e:
        st.error(f"🚫 Error reading `{latest_file}`: {e}")
else:
    st.info("No output files found yet. Run an assistant to generate results.")

# ✅ Assistant-specific output archive (detailed history for the selected assistant)
st.markdown("---")
st.subheader("🗂️ Output Archive for Selected Assistant")
if task_type:
    assistant_output_dir = os.path.join(OUTPUT_DIR, task_type)
    if os.path.isdir(assistant_output_dir):
        output_files = sorted(os.listdir(assistant_output_dir), reverse=True)
        for fname in output_files:
            file_path = os.path.join(assistant_output_dir, fname)
            if fname.endswith(".csv"):
                with st.expander(f"📊 CSV: {fname}"):
                    try:
                        df = pd.read_csv(file_path)
                        st.dataframe(df.head())
                        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=fname)
                    except Exception as e:
                        st.warning(f"⚠️ Could not preview `{fname}`: {e}")
            elif fname.endswith((".yaml", ".yml")):
                with st.expander(f"📐 YAML: {fname}"):
                    try:
                        text = open(file_path, "r").read()
                        st.code(text, language="yaml")
                        st.download_button("⬇️ Download YAML", text, file_name=fname)
                    except Exception as e:
                        st.warning(f"⚠️ Could not read `{fname}`: {e}")
            elif fname.endswith(".md"):
                with st.expander(f"📝 Notes: {fname}"):
                    try:
                        text = open(file_path, "r").read()
                        st.markdown(text)
                        st.download_button("⬇️ Download .md", text, file_name=fname)
                    except Exception as e:
                        st.warning(f"⚠️ Could not read `{fname}`: {e}")
            else:
                # Generic file type
                with st.expander(f"📁 File: {fname}"):
                    st.markdown(f"Stored at: `{file_path}`")
                    try:
                        data = open(file_path, "rb").read()
                        st.download_button("⬇️ Download", data, file_name=fname)
                    except Exception as e:
                        st.write(f"*(Unable to read file: {e})*")
    else:
        st.info(f"No outputs found yet for assistant `{task_type}`.")

# ✅ Run history & bundled exports (group outputs by run timestamp and allow bulk download)
st.markdown("## 🕒 Run History & Bundled Exports")
if task_type and os.path.isdir(os.path.join(OUTPUT_DIR, task_type)):
    files = sorted(os.listdir(os.path.join(OUTPUT_DIR, task_type)), reverse=True)
    # Group files by shared timestamp in filename (assumes filenames contain a timestamp segment)
    grouped_runs = {}
    for fname in files:
        # Assume timestamp is last part of filename before extension (after last underscore)
        run_id = fname.split("_")[-1].split(".")[0]
        grouped_runs.setdefault(run_id, []).append(fname)
    for run_id, file_list in grouped_runs.items():
        with st.expander(f"🧾 Run {run_id} ({len(file_list)} files)"):
            st.markdown("**Files:** " + ", ".join(file_list))
            # Prepare ZIP in-memory for this run
            import io, zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for fname in file_list:
                    fpath = os.path.join(OUTPUT_DIR, task_type, fname)
                    if os.path.isfile(fpath):
                        zf.write(fpath, arcname=fname)
            zip_buffer.seek(0)
            st.download_button(
                label=f"⬇️ Download All ({len(file_list)})",
                data=zip_buffer,
                file_name=f"{task_type}_run_{run_id}.zip",
                mime="application/zip"
            )
else:
    st.info("No run history available yet.")

# ✅ Sidebar: Assistant Uploader and Output Export components
st.sidebar.markdown("---")
import upload_zone  # integrates the assistant/script upload UI in sidebar
import output_export  # integrates the output export UI in sidebar

# ✅ Sidebar: System Health & Last-Run Status
st.sidebar.markdown("---")
st.sidebar.markdown("### 🩺 System Status")
# Count of assistants available
st.sidebar.write(f"**Assistants loaded:** {len(assistant_types)}")
# Google Drive credential status
cred_status = "✅ Loaded" if os.path.exists("client_secret.json") else "⚠️ Not provided"
st.sidebar.write(f"**Google Drive credential:** {cred_status}")
# Last run status summary
if 'last_run' in st.session_state:
    lr = st.session_state.last_run
    if lr.get("status_code") is None:
        st.sidebar.write(f"**Last run:** ❌ *Failed to reach API* at {lr.get('time')}")
    elif lr["status_code"] != 200:
        st.sidebar.write(f"**Last run:** ❌ *API error (HTTP {lr['status_code']})* at {lr['time']}")
    else:
        # API returned 200, check assistant output status
        out_status = ""
        if lr["result_json"]:
            out_status = lr["result_json"].get("output", {}).get("status", "")
        if out_status.startswith("✅"):
            st.sidebar.write(f"**Last run:** ✅ *{lr['assistant']}* succeeded at {lr['time']}")
        elif out_status.startswith("❌"):
            st.sidebar.write(f"**Last run:** ❌ *{lr['assistant']}* failed at {lr['time']}")
        else:
            st.sidebar.write(f"**Last run:** *{lr['assistant']}* completed at {lr['time']}")
        # If error details present, show a snippet
        error_msg = None
        if lr["result_json"]:
            error_msg = lr["result_json"].get("output", {}).get("error")
        if error_msg:
            st.sidebar.caption(f"Last error: {error_msg}")
else:
    st.sidebar.write("**Last run:** *(no runs yet)*")

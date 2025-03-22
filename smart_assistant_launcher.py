import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ✅ Streamlit UI setup
st.set_page_config(page_title="🧠 Smart Assistant Launcher", layout="centered")
st.title("🧠 Smart Assistant Launcher")

# ✅ Upload Google Credentials
st.sidebar.subheader("🔐 Upload Google Credentials")
creds_file = st.sidebar.file_uploader("Upload your Google Drive client_secret.json", type="json")
if creds_file:
    with open("client_secret.json", "wb") as f:
        f.write(creds_file.read())

# ✅ Google Drive Upload Helper
def upload_to_drive(file_path, file_name):
    creds = service_account.Credentials.from_service_account_file(
        "client_secret.json", scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": file_name, "parents": ["root"]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return f"https://drive.google.com/file/d/{uploaded_file['id']}/view"

# ✅ Assistant Selector
st.markdown("## ⚙️ Assistant Type")
ASSISTANT_DIR = "assistants"
os.makedirs(ASSISTANT_DIR, exist_ok=True)
try:
    assistant_types = sorted([
        f.replace(".py", "") for f in os.listdir(ASSISTANT_DIR)
        if f.endswith(".py") and not f.startswith("__")
    ])
except Exception as e:
    assistant_types = []
    st.warning(f"⚠️ Error loading assistants: {e}")

if assistant_types:
    task_type = st.selectbox("Choose Assistant", assistant_types)
else:
    task_type = None
    st.warning("⚠️ No assistants found in /assistants directory.")

# ✅ Assistant Config Form
with st.form("assistant_form"):
    prompt = st.text_input("Prompt", "Scrape latest laptops from Newegg with prices and ratings")
    url = st.text_input("Target URL", "https://www.newegg.com/laptops")
    filters = st.text_input("Filters (comma-separated)", "price, rating")

    # Assistant-specific UI
    if task_type == "kep_extractor":
        st.header("📘 KEP Extractor Inputs")
        course_title = st.text_input("Course Title")
        module_title = st.text_input("Module Title")
        lesson_input = st.text_area("Lesson Titles (comma-separated)")
        lesson_titles = [l.strip() for l in lesson_input.split(",") if l.strip()]
    elif task_type == "blueprint_generator":
        st.header("📐 Blueprint Generator")
        uploaded_csv = st.file_uploader("Upload KEP CSV", type="csv")

    submitted = st.form_submit_button("💾 Save Config to Drive & Trigger Assistant")

    if submitted and task_type:
        config_data = {
            "task_type": task_type,
            "prompt": prompt,
            "url": url,
            "filters": filters,
            "timestamp": datetime.now().isoformat()
        }

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

        filename = f"assistant_config_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(config_data, f, indent=4)

        try:
            drive_link = upload_to_drive(filename, filename)
            st.success("✅ Config uploaded to Google Drive!")
            st.markdown(f"[📄 View on Google Drive]({drive_link})")

            api_url = "https://assistant-api-pzj8.onrender.com/run-assistant"
            try:
                res = requests.post(api_url, json=config_data)
                if res.status_code == 200:
                    st.success("📬 Assistant triggered successfully!")
                    st.json(res.json())
                else:
                    st.error(f"❌ Webhook failed: {res.status_code}")
                    st.text(res.text)
            except Exception as e:
                st.error(f"❌ Webhook error: {e}")

        except Exception as e:
            st.error(f"❌ Drive upload failed: {e}")

# ✅ Output Preview (safe fallback)

os.makedirs("output/web_scraper", exist_ok=True)

st.markdown("---")
st.subheader("📄 Latest Output Preview")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
latest_outputs = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")], reverse=True)

if latest_outputs:
    latest_file = latest_outputs[0]
    st.markdown(f"📁 Showing latest output: `{latest_file}`")
    try:
        df = pd.read_csv(os.path.join(OUTPUT_DIR, latest_file))
        st.dataframe(df.head(10))
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=latest_file)
    except pd.errors.EmptyDataError:
        st.warning(f"⚠️ `{latest_file}` is empty or malformed — no columns to preview.")
    except Exception as e:
        st.error(f"🚫 Error loading preview: {e}")
else:
    st.info("No output files found yet. Run the assistant to generate results.")


# 🔍 Assistant-specific output preview
st.markdown("---")
st.subheader("🧠 Assistant Output Archive")

if task_type:
    assistant_output_dir = os.path.join("output", task_type)
    if os.path.exists(assistant_output_dir):
        output_files = sorted(os.listdir(assistant_output_dir), reverse=True)
        for f in output_files:
            file_path = os.path.join(assistant_output_dir, f)
            if f.endswith(".csv"):
                with st.expander(f"📊 CSV: {f}"):
                    try:
                        df = pd.read_csv(file_path)
                        st.dataframe(df.head())
                        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=f)
                    except Exception as e:
                        st.warning(f"⚠️ Could not preview CSV: {e}")
            elif f.endswith(".yaml") or f.endswith(".yml"):
                with st.expander(f"📐 YAML: {f}"):
                    with open(file_path, "r") as file:
                        st.code(file.read(), language="yaml")
            elif f.endswith(".md"):
                with st.expander(f"📝 Notes: {f}"):
                    with open(file_path, "r") as file:
                        st.markdown(file.read())
            else:
                with st.expander(f"📁 File: {f}"):
                    st.markdown(f"🗂️ Stored at: `{file_path}`")
    else:
        st.info(f"No outputs found for assistant: `{task_type}`")

import zipfile
import io

st.markdown("## 🕒 Run History & Bundled Exports")

history_root = os.path.join("output", task_type) if task_type else None

if history_root and os.path.exists(history_root):
    all_files = sorted(os.listdir(history_root), reverse=True)
    grouped = {}

    # Group by date prefix (e.g., shared timestamp)
    for f in all_files:
        key = f.split("_")[-1].split(".")[0]  # timestamp portion
        grouped.setdefault(key, []).append(f)

    for run_id, files in grouped.items():
        with st.expander(f"🧾 Run {run_id} ({len(files)} file(s))"):
            st.markdown("**Files:**")
            for f in files:
                st.markdown(f"🔹 {f}")

            # Download all files from this run as a ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for f in files:
                    f_path = os.path.join(history_root, f)
                    zf.write(f_path, arcname=f)
            zip_buffer.seek(0)
            st.download_button(
                label=f"⬇️ Download All ({len(files)} files)",
                data=zip_buffer,
                file_name=f"{task_type}_run_{run_id}.zip",
                mime="application/zip"
            )
else:
    st.info("No saved runs yet for this assistant.")

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
    submitted = st.form_submit_button("💾 Save Config to Drive & Trigger Assistant")

    if submitted and task_type:
        config_data = {
            "task_type": task_type,
            "prompt": prompt,
            "url": url,
            "filters": filters,
            "timestamp": datetime.now().isoformat()
        }
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

# ✅ Output Preview
st.markdown("---")
st.subheader("📄 Latest Output Preview")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
latest_outputs = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")], reverse=True)
if latest_outputs:
    latest_file = latest_outputs[0]
    st.markdown(f"📁 Showing latest output: `{latest_file}`")
    df = pd.read_csv(os.path.join(OUTPUT_DIR, latest_file))
    st.dataframe(df.head(10))
    st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=latest_file)
else:
    st.info("No output files found yet. Run the assistant to generate results.")

# ✅ Config & Output History
st.markdown("---")
st.subheader("🗂️ Config & Output History")
CONFIG_DIR = "configs"
os.makedirs(CONFIG_DIR, exist_ok=True)
all_configs = sorted([f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")], reverse=True)
all_outputs = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")], reverse=True)

st.markdown("### Saved Configs")
for cfg in all_configs:
    with open(os.path.join(CONFIG_DIR, cfg)) as f:
        cfg_data = json.load(f)
    with st.expander(cfg):
        st.json(cfg_data)
        st.download_button("⬇️ Download Config", json.dumps(cfg_data, indent=2), file_name=cfg)

st.markdown("### Saved Outputs")
for out in all_outputs:
    with st.expander(out):
        df = pd.read_csv(os.path.join(OUTPUT_DIR, out))
        st.dataframe(df.head(5))
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=out)

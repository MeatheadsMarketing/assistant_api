import streamlit as st
import json
import os
import requests
from datetime import datetime

st.set_page_config(page_title="🔗 Modular Assistant Chainer (SPG)", layout="wide")
st.title("🔗 Modular Assistant Chainer")
st.subheader("🧠 Assistant Chain")

CHAIN_DIR = "config"
OUTPUT_DIR = "output"

# Number of assistants in the chain
num_assistants = st.slider("Number of Assistants to Chain", min_value=2, max_value=5, value=2)

configs = []

# Upload configs and display
for i in range(num_assistants):
    with st.expander(f"Assistant {i+1} Config"):
        uploaded = st.file_uploader(f"Upload Config for Assistant {i+1}", type="json", key=f"uploader_{i}")
        if uploaded:
            config = json.load(uploaded)
            configs.append(config)
            st.json(config)

# Chaining logic
if st.button("🚀 Run Assistant Chain") and len(configs) == num_assistants:
    output = None
    metadata = []

    for idx, config in enumerate(configs):
        assistant = config.get("task_type", "unknown")

        if output:
            config["chained_input"] = output  # pass output to next config

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_filename = f"chained_config_{assistant}_{timestamp}.json"

        with open(os.path.join(CHAIN_DIR, config_filename), "w") as f:
            json.dump(config, f, indent=2)

        try:
            response = requests.post("http://localhost:8000/run-assistant", json=config)
            if response.status_code == 200:
                result = response.json()
                output = result.get("output")
                st.success(f"✅ Assistant {idx+1} ({assistant}) completed.")
                st.json(result)

                output_file = f"chained_output_{assistant}_{timestamp}.json"
                with open(os.path.join(OUTPUT_DIR, output_file), "w") as f:
                    json.dump(result, f, indent=2)

                metadata.append({
                    "assistant": assistant,
                    "output_file": output_file,
                    "timestamp": timestamp
                })
            else:
                st.error(f"❌ Assistant {idx+1} failed: {response.text}")
                break
        except Exception as e:
            st.error(f"❌ Error running assistant {idx+1}: {e}")
            break

    # Log metadata
    chain_log = f"chain_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(OUTPUT_DIR, chain_log), "w") as f:
        json.dump(metadata, f, indent=2)

    st.info("🔁 Chain complete.")
    st.json(metadata)


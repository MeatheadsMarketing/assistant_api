import streamlit as st
import os
import pandas as pd
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="📊 Table Parser Assistant", layout="wide")
st.title("📊 Advanced Table Parser (SPG Tier 2)")

# Section: Upload or paste raw HTML/text
txt_data = st.text_area("Paste raw HTML, Markdown, or messy table-like content", height=300)

# Section: HTML Table Detection
parsed_tables = []
if st.checkbox("🔍 Detect and extract HTML <table> blocks"):
    try:
        soup = BeautifulSoup(txt_data, "html.parser")
        tables = soup.find_all("table")
        parsed_tables = [pd.read_html(str(tbl))[0] for tbl in tables]
        table_options = [f"Table {i+1} ({len(tbl)} rows)" for i, tbl in enumerate(parsed_tables)]
        selected_table = st.selectbox("Choose a table to parse:", table_options)
        if parsed_tables:
            df = parsed_tables[table_options.index(selected_table)]
    except Exception as e:
        st.error(f"❌ HTML parsing failed: {e}")
        df = pd.DataFrame()
else:
    # Basic Delimiter Fallback
    parser_mode = st.selectbox("Choose parsing strategy", ["regex", "split lines"])
    delimiter = st.text_input("Optional delimiter (if using split)", value="|")
    expected_cols = st.text_input("Expected columns (comma-separated)", value="title,price,rating")

    rows = []
    lines = txt_data.strip().split("\n")
    for line in lines:
        parts = [part.strip() for part in line.split(delimiter)]
        if len(parts) >= 2:
            rows.append(parts)
    df = pd.DataFrame(rows)
    if expected_cols:
        df.columns = [col.strip() for col in expected_cols.split(",")[:len(df.columns)]]

# Inference toggle
if not df.empty and st.checkbox("🧠 Auto-detect column types"):
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
        df[col] = pd.to_datetime(df[col], errors='ignore')

# Preview
if not df.empty:
    st.success("✅ Table parsed successfully")
    st.dataframe(df.head())

    # Save output format
    out_format = st.selectbox("Export format", ["CSV", "JSON", "Markdown"])
    summarize = st.checkbox("🧠 Generate summary snippet")
    config_label = st.text_input("Optional Config Label", "table_parse_config")

    if st.button("💾 Save Output & Config"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"table_parser_output_{ts}"
        os.makedirs("output", exist_ok=True)

        if out_format == "CSV":
            path = f"output/{fname}.csv"
            df.to_csv(path, index=False)
        elif out_format == "JSON":
            path = f"output/{fname}.json"
            df.to_json(path, orient="records", indent=2)
        elif out_format == "Markdown":
            path = f"output/{fname}.md"
            with open(path, "w") as f:
                f.write(df.head().to_markdown(index=False))

        st.success(f"✅ Saved: {path}")
        st.download_button("📥 Download Output", open(path, "rb"), file_name=os.path.basename(path))

        # Save config
        config_data = {
            "parser_mode": parser_mode,
            "expected_cols": expected_cols,
            "delimiter": delimiter,
            "auto_type": True,
            "format": out_format
        }
        with open(f"config/{config_label}.json", "w") as f:
            json.dump(config_data, f, indent=2)
        st.caption(f"🧾 Config saved as config/{config_label}.json")

        if summarize:
            summary = f"Parsed {len(df)} rows with {len(df.columns)} columns."
            st.markdown(f"### 📌 Summary\n{summary}")
else:
    st.warning("⚠️ No valid table content found to parse.")


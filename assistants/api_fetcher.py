import os
import requests
import pandas as pd
from datetime import datetime

def run(config):
    url = config.get("url")
    filters = [f.strip() for f in config.get("filters", "").split(",")]

    try:
        response = requests.get(url)
        data = response.json()

        df = pd.json_normalize(data)
        if filters:
            df = df[filters]

        out_dir = "output/api_fetcher"
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{out_dir}/api_fetcher_output_20250322_143513.csv"
        df.to_csv(filename, index=False)

        return {
            "status": "✅ Success",
            "outputs": [filename]
        }
    except Exception as e:
        return {"status": "❌ Failed", "error": str(e)}
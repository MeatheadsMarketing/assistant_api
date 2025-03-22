import requests
import pandas as pd
from datetime import datetime
import os

def run_api_fetcher(config):
    endpoint = config.get("url")  # Treat as API endpoint
    filters = [f.strip() for f in config.get("filters", "").split(",")]
    
    try:
        response = requests.get(endpoint)
        data = response.json()

        # Convert to DataFrame (assumes list of dicts)
        df = pd.DataFrame(data)
        
        # Optional: filter columns
        if filters:
            df = df[[col for col in filters if col in df.columns]]

        # Save output
        os.makedirs("output", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"api_fetcher_output_{timestamp}.csv"
        df.to_csv(f"output/{filename}", index=False)
        return filename

    except Exception as e:
        return f"❌ Failed to fetch/process API: {e}"
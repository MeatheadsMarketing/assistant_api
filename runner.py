import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def run_assistant(config):
    if config.get("task_type") == "web_scraper":
        url = config["url"]
        filters = [f.strip() for f in config["filters"].split(",")]

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        items = []
        for item in soup.select(".item-cell"):
            title = item.select_one(".item-title")
            price = item.select_one(".price-current")

            row = {
                "title": title.text.strip() if title else None,
                "price": price.text.strip() if price else None,
            }

            filtered = {k: v for k, v in row.items() if k in filters or not filters}
            items.append(filtered)

        df = pd.DataFrame(items)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs("output", exist_ok=True)
        filename = f"web_scraper_output_{timestamp}.csv"
        df.to_csv(f"output/{filename}", index=False)
        return filename
    else:
        return "❌ Unsupported task_type"
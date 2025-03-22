import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def run(config):
    url = config.get("url")
    filters = [f.strip() for f in config.get("filters", "").split(",")]
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        items = []
        for item in soup.select(".item-cell"):
            title = item.select_one(".item-title")
            price = item.select_one(".price-current")
            rating = item.select_one(".item-rating")
            row = {
                "title": title.text.strip() if title else None,
                "price": price.text.strip() if price else None,
                "rating": rating['title'] if rating and rating.has_attr("title") else None
            }
            filtered = {k: v for k, v in row.items() if k in filters}
            items.append(filtered)

        df = pd.DataFrame(items)
        out_dir = "output/web_scraper"
        os.makedirs(out_dir, exist_ok=True)
	out_dir = "output/web_scraper"
	os.makedirs(out_dir, exist_ok=True)
	filename = f"{out_dir}/web_scraper_output_{timestamp}.csv"
        df.to_csv(filename, index=False)

        return {
            "status": "✅ Success",
            "outputs": [filename]
        }

    except Exception as e:
        return {"status": "❌ Failed", "error": str(e)}

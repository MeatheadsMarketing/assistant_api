
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

def run_web_scraper(config):
    url = config.get("url")
    filters = config.get("filters", "")
    keywords = [f.strip().lower() for f in filters.split(",") if f.strip()]
    timestamp = config.get("timestamp", datetime.now().isoformat())
    
    output_dir = "output/web_scraper"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"web_scraper_output_{timestamp.replace(':', '').replace('-', '').replace('T', '_')}.csv"
    filepath = os.path.join(output_dir, filename)

    try:
        print(f"🌐 Fetching: {url}")
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        items = []
        for container in soup.select(".item-cell"):
            title_elem = container.select_one(".item-title")
            price_elem = container.select_one(".price-current")

            if not title_elem:
                continue

            title = title_elem.text.strip()
            price = price_elem.text.strip() if price_elem else "N/A"

            if keywords:
                matched = any(k in title.lower() for k in keywords)
                if not matched:
                    continue

            items.append({
                "title": title,
                "price": price,
                "timestamp": timestamp
            })

        if items:
            df = pd.DataFrame(items)
            df.to_csv(filepath, index=False)
            print(f"✅ Saved {len(df)} items to {filename}")
            return {"status": "✅ Success", "outputs": [filename]}
        else:
            print("⚠️ No matching items found.")
            return {"status": "⚠️ No results matched filters", "outputs": []}

    except Exception as e:
        print("❌ Scraper error:", str(e))
        return {"status": "❌ Failed", "error": str(e)}

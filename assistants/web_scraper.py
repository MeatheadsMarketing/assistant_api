# ✅ Web Scraper Assistant v3 with Tier 3 - Batch 2 Upgrades

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
import json
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime
from random import choice
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def rotate_headers():
    headers = [
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/122.0"},
    ]
    return choice(headers)


def load_proxies():
    try:
        with open("proxies.json") as f:
            proxy_list = json.load(f)
        return proxy_list
    except:
        return []


def normalize_text(text):
    return re.sub(r'\s+', ' ', text.strip())


def clean_price(price):
    return float(price.replace("$", "").strip()) if price else None

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_with_requests(url, headers, proxy=None):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    return requests.get(url, headers=headers, timeout=10, proxies=proxies)


def fetch_with_browser(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


def run_web_scraper(config):
    url = config.get("url")
    filters = [f.strip().lower() for f in config.get("filters", "").split(",") if f.strip()]
    prompt = config.get("prompt")
    pages = int(config.get("pages", 1))
    selector_config_path = config.get("selectors", "selectors.json")
    use_browser = config.get("use_browser", False)
    callback_url = config.get("callback_url")

    if not is_valid_url(url):
        return {"status": "❌ Invalid URL", "output": None}

    try:
        with open(selector_config_path) as sel:
            selectors = json.load(sel)
    except:
        selectors = {"item": "div", "title": ".title", "price": ".price"}

    headers = rotate_headers()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output = f"web_scraper_output_{run_id}"
    output_dir = "output"
    archive_dir = os.path.join("archive", "web_scraper", run_id)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    all_rows = []
    start_time = time.time()
    proxies = load_proxies()

    for page in range(1, pages + 1):
        page_url = f"{url}?page={page}" if page > 1 else url
        try:
            if use_browser:
                html = fetch_with_browser(page_url)
            else:
                proxy = choice(proxies) if proxies else None
                res = fetch_with_requests(page_url, headers, proxy)
                html = res.text

            soup = BeautifulSoup(html, "html.parser")
            items = soup.select(selectors.get("item", "div"))

            for item in items:
                title_el = item.select_one(selectors.get("title", ""))
                price_el = item.select_one(selectors.get("price", ""))
                title = normalize_text(title_el.text) if title_el else ""
                price = normalize_text(price_el.text) if price_el else ""

                if all(f in title.lower() for f in filters):
                    row = {
                        "title": title,
                        "price": clean_price(price),
                        "page": page
                    }
                    all_rows.append(row)
        except Exception as e:
            return {"status": f"❌ Failed on page {page}: {e}", "output": None}

    if not all_rows:
        return {"status": "⚠️ No matching content found across pages", "output": None}

    df = pd.DataFrame(all_rows)
    csv_file = os.path.join(output_dir, f"{base_output}.csv")
    md_file = os.path.join(output_dir, f"{base_output}_summary.md")
    df.to_csv(csv_file, index=False)

    preview = df.head(5).to_markdown(index=False)
    with open(md_file, "w") as md:
        md.write(f"## Web Scraper Summary\nGenerated: {run_id}\n\n")
        md.write(preview)

    # Save metadata
    metadata = {
        "status": "✅ Success",
        "run_id": run_id,
        "assistant": "web_scraper",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "records": len(all_rows),
        "pages_scraped": pages,
        "output_file": csv_file,
        "summary_md": md_file
    }

    with open(os.path.join(archive_dir, "run_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Save full archive output copies
    df.to_csv(os.path.join(archive_dir, f"{base_output}.csv"), index=False)
    with open(os.path.join(archive_dir, f"{base_output}_summary.md"), "w") as f:
        f.write(preview)

    # Webhook callback
    if callback_url:
        try:
            requests.post(callback_url, json=metadata)
        except Exception as e:
            metadata["callback_error"] = str(e)

    return metadata


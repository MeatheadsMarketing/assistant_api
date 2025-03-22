import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def run_assistant(config):
    task_type = config.get("task_type")

    if task_type == "web_scraper":
        from web_scraper import run_web_scraper
        return run_web_scraper(config)

    elif task_type == "api_fetcher":
        from assistants.api_fetcher import run_api_fetcher
        return run_api_fetcher(config)

    else:
        return "❌ Unsupported task_type"
# Assistant API (Webhook Trigger)

This is a FastAPI-based backend to trigger assistant execution (e.g., web scraper) via a webhook.

## Endpoints

### POST /run-assistant
Trigger an assistant run with a JSON config payload.

**Example Payload:**
```json
{
  "task_type": "web_scraper",
  "prompt": "Scrape laptops from Newegg",
  "url": "https://www.newegg.com/laptops",
  "filters": "price, rating",
  "timestamp": "2025-03-21T22:45:00"
}
```

## How to Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Output CSVs will be saved to `/output/`, and configs to `/config/`.
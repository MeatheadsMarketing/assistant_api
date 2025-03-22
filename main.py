from pydantic import BaseModel
from fastapi import FastAPI, Request
from runner import run_assistant
import os, json
from pydantic import BaseModel

class AssistantConfig(BaseModel):
    task_type: str
    prompt: str
    url: str
    filters: str
    timestamp: str

    class Config:
        schema_extra = {
            "example": {
                "task_type": "web_scraper",
                "prompt": "Scrape laptops from Newegg",
                "url": "https://www.newegg.com/laptops",
                "filters": "price, rating",
                "timestamp": "2025-03-22T02:00:00"
            }
        }


app = FastAPI()

@app.post("/run-assistant")
async def run(config: AssistantConfig):
    config = config.dict()
    print("📥 Received config:", config)

    os.makedirs("config", exist_ok=True)
    filename = f"config_{config.get('task_type')}_{config.get('timestamp', 'now')}.json"
    with open(f"config/{filename}", "w") as f:
        json.dump(config, f, indent=4)

    result = run_assistant(config)
    return {"status": "✅ Success", "output": result}
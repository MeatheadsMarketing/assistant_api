
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from runner import run_assistant
import os, json
from datetime import datetime
from enum import Enum

# Setup
app = FastAPI()

# Enable full CORS for webhook access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting to Streamlit domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define task types
class TaskType(str, Enum):
    web_scraper = "web_scraper"
    api_fetcher = "api_fetcher"
    assistant_chainer = "assistant_chainer"

# Define the config model
class AssistantConfig(BaseModel):
    task_type: TaskType
    prompt: str
    url: str = ""
    filters: str = ""
    timestamp: str = datetime.now().isoformat()

    class Config:
        schema_extra = {
            "example": {
                "task_type": "web_scraper",
                "prompt": "Scrape latest laptops from Newegg",
                "url": "https://www.newegg.com/laptops",
                "filters": "price, rating",
                "timestamp": "2025-03-22T00:00:00"
            }
        }

# Main execution route
@app.post("/run-assistant")
async def run(request: Request):
    config = await request.json()
    print("🧠 Received config:", config)
    
    # Save config to disk
    os.makedirs("config", exist_ok=True)
    filename = f"config_{config.get('task_type', 'unknown')}_{config.get('timestamp').replace(':','').replace('-','').replace('T','_')}.json"
    with open(os.path.join("config", filename), "w") as f:
        json.dump(config, f, indent=4)

    result = run_assistant(config)
    return {"status": "✅ Success", "output": result}

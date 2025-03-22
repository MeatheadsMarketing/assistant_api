# main.py - Step-by-step refactor with 10 elite-level enhancements

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from runner import run_assistant
from enum import Enum
import os, json
from datetime import datetime
from uuid import uuid4

# 1️⃣ Add CORS middleware with domain restriction
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://assistantapi.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2️⃣ Define task type with extensible enums
class TaskType(str, Enum):
    web_scraper = "web_scraper"
    api_fetcher = "api_fetcher"
    assistant_chainer = "assistant_chainer"

# 3️⃣ Add request model with built-in validation
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
                "prompt": "Scrape laptops from Newegg",
                "url": "https://www.newegg.com/laptops",
                "filters": "price, rating",
                "timestamp": "2025-03-22T00:00:00"
            }
        }

# 4️⃣ Add custom exception handler for validation errors
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "❌ Validation Failed", "errors": exc.errors()},
    )

# 5️⃣ Generate a request_id for logging
@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

# 6️⃣ Expose available assistants as metadata
@app.get("/assistants")
async def get_assistant_list():
    return {"available": [task.value for task in TaskType]}

# 7️⃣ Add execution API endpoint with robust logging
@app.post("/run-assistant")
async def run(request: Request):
    try:
        config = await request.json()
        print(f"🧠 Request ID: {request.state.request_id} | Received config:", config)

        # 8️⃣ Filename-safe formatter
        os.makedirs("config", exist_ok=True)
        timestamp = config.get('timestamp', datetime.now().isoformat())
        safe_timestamp = timestamp.replace(':','').replace('-','').replace('T','_')
        filename = f"config_{config.get('task_type', 'unknown')}_{safe_timestamp}.json"
        filepath = os.path.join("config", filename)

        # 9️⃣ Config auto-save
        with open(filepath, "w") as f:
            json.dump(config, f, indent=4)

        # 🔟 Run assistant and return result
        result = run_assistant(config)
        return {
            "status": "✅ Success",
            "request_id": request.state.request_id,
            "config_file": filename,
            "result": result
        }

    except Exception as e:
        print(f"❌ Request ID: {request.state.request_id} | Internal error:", str(e))
        return JSONResponse(status_code=500, content={"status": "❌ Failed", "error": str(e)})

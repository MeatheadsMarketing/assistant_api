from fastapi import FastAPI, Request
from runner import run_assistant
import os, json

app = FastAPI()

@app.post("/run-assistant")
async def run(request: Request):
    config = await request.json()
    print("📥 Received config:", config)

    # Save config file
    os.makedirs("config", exist_ok=True)
    filename = f"config_{config.get('task_type')}_{config.get('timestamp', 'now')}.json"
    with open(f"config/{filename}", "w") as f:
        json.dump(config, f, indent=4)

    # Run assistant logic
    result = run_assistant(config)
    return {"status": "✅ Success", "output": result}
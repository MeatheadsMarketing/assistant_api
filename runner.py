
import os
import json
from datetime import datetime

ASSISTANT_REGISTRY = {
    "web_scraper": "assistants.web_scraper.run_web_scraper",
    "api_fetcher": "assistants.api_fetcher.run_api_fetcher",
    "assistant_chainer": "assistants.assistant_chainer.run_assistant_chainer",
}

def run_assistant(config):
    task_type = config.get("task_type")
    try:
        module_path, func_name = ASSISTANT_REGISTRY[task_type].rsplit(".", 1)
        module = __import__(module_path, fromlist=[func_name])
        runner = getattr(module, func_name)
        result = runner(config)

        # log history
        output_dir = os.path.join("output", task_type)
        os.makedirs(output_dir, exist_ok=True)
        history_path = os.path.join(output_dir, "history.json")
        history = []
        if os.path.exists(history_path):
            with open(history_path) as f:
                history = json.load(f)

        history.append({
            "timestamp": config.get("timestamp", datetime.now().isoformat()),
            "prompt": config.get("prompt"),
            "filters": config.get("filters"),
            "file": result.get("outputs", [None])[0]
        })

        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)

        return result
    except Exception as e:
        print("❌ Assistant dispatch failed:", e)
        return {"status": "❌ Failed", "error": str(e)}

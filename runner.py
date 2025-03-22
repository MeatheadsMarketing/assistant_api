import os
import json
import uuid
import zipfile
from datetime import datetime
from importlib import import_module
from difflib import get_close_matches
from pathlib import Path
from typing import Any

# 1️⃣ Load assistant registry from JSON metadata
try:
    with open("registry.json") as f:
        ASSISTANT_REGISTRY = json.load(f)
except FileNotFoundError:
    ASSISTANT_REGISTRY = {
        "web_scraper": "assistants.web_scraper.run_web_scraper",
        "api_fetcher": "assistants.api_fetcher.run_api_fetcher",
        "assistant_chainer": "assistants.assistant_chainer.run_assistant_chainer",
    }

# 8️⃣ Generate run ID per execution
def generate_run_id():
    return uuid.uuid4().hex[:8]

# 10️⃣ Retry decorator
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def safe_run(func, config):
    return func(config)

# Core runner
def run_assistant(config: dict[str, Any]) -> dict[str, Any]:
    run_id = generate_run_id()
    task_type = config.get("task_type")
    config["run_id"] = run_id

    # 6️⃣ Failback task_type resolution if missing
    if task_type not in ASSISTANT_REGISTRY:
        suggestions = get_close_matches(task_type, ASSISTANT_REGISTRY.keys())
        return {
            "status": "❌ Unknown task_type",
            "suggestions": suggestions
        }

    # 1️⃣ Dynamic loader
    module_path, func_name = ASSISTANT_REGISTRY[task_type].rsplit(".", 1)
    try:
        module = import_module(module_path)
        runner_func = getattr(module, func_name)
    except Exception as e:
        return {"status": "❌ Failed to load assistant", "error": str(e)}

    try:
        # 10️⃣ Retry wrapped runner execution
        result = safe_run(runner_func, config)

        # 5️⃣ Log run details to jsonl
        Path("logs").mkdir(exist_ok=True)
        with open("logs/run_log.jsonl", "a") as log:
            log.write(json.dumps({
                "run_id": run_id,
                "task_type": task_type,
                "timestamp": config.get("timestamp"),
                "status": result.get("status"),
                "output": result.get("outputs", [])
            }) + "\n")

        # 9️⃣ Archive output if available
        if result.get("outputs"):
            archive_dir = Path("archive") / task_type
            archive_dir.mkdir(parents=True, exist_ok=True)
            zip_path = archive_dir / f"{run_id}.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in result["outputs"]:
                    if file and os.path.exists(file):
                        zipf.write(file, arcname=os.path.basename(file))

        # 2️⃣ Wrap all responses in standard format
        return {
            "status": result.get("status", "✅ Success"),
            "run_id": run_id,
            "task_type": task_type,
            "outputs": result.get("outputs", []),
            "metadata": result.get("metadata", {})
        }

    except Exception as e:
        return {"status": "❌ Assistant execution failed", "error": str(e)}

# 7️⃣ Ping all assistants for health check
def check_registry_health():
    health = {}
    for key, path in ASSISTANT_REGISTRY.items():
        try:
            module_path, func_name = path.rsplit(".", 1)
            module = import_module(module_path)
            getattr(module, func_name)
            health[key] = "✅ Ready"
        except:
            health[key] = "❌ Missing or broken"
    return health


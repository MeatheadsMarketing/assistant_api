import importlib
import os, json

def run_assistant(config: dict):
    """Dynamically dispatches the assistant based on config['task_type']."""
    task_type = config.get("task_type")
    try:
        module = importlib.import_module(f"assistants.{task_type}")
    except ImportError as e:
        return {"status": "❌ Failed", "error": f"Assistant '{task_type}' not found: {e}"}
    if not hasattr(module, "run"):
        return {"status": "❌ Failed", "error": f"Assistant '{task_type}' has no run() function"}
    # Run the assistant's main function
    try:
        result = module.run(config)
    except Exception as e:
        # Catch any exception during execution
        print(f"❌ Exception in {task_type}: {e}")
        return {"status": "❌ Failed", "error": str(e)}
    # Determine output file names (if any) from the result
    output_files = []
    if isinstance(result, dict):
        if "outputs" in result:
            output_files = result["outputs"]
        elif "output_file" in result:
            output_files = [result["output_file"]]
        elif isinstance(result.get("output"), str):
            output_files = [result["output"]]
    elif isinstance(result, str):
        output_files = [result]
    # Log history of this run
    history_dir = os.path.join("output", task_type)
    os.makedirs(history_dir, exist_ok=True)
    history_path = os.path.join(history_dir, "history.json")
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
    history.append({
        "timestamp": config.get("timestamp"),
        "prompt": config.get("prompt"),
        "outputs": output_files
    })
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    return result

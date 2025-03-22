import os
import pandas as pd
from datetime import datetime
import yaml

def run(config):
    try:
        source_path = config.get("uploaded_kep_csv")
        df = pd.read_csv(source_path)

        blueprint = {
            "assistant_blueprint": []
        }
        for _, row in df.iterrows():
            blueprint["assistant_blueprint"].append({
                "lesson": row.get("Lesson", ""),
                "task": f"Define tasks for {row.get('Topic', '')}"
            })

        out_dir = "output/blueprint_generator"
        os.makedirs(out_dir, exist_ok=True)
        blueprint_file = f"{out_dir}/blueprint_20250322_143513.yaml"
        with open(blueprint_file, "w") as f:
            yaml.dump(blueprint, f, sort_keys=False)

        return {
            "status": "✅ Success",
            "outputs": [blueprint_file]
        }
    except Exception as e:
        return {"status": "❌ Failed", "error": str(e)}
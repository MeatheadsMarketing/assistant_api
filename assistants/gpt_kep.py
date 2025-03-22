import os
import pandas as pd
from datetime import datetime

def run(config):
    lessons = config.get("lesson_titles", [])
    course = config.get("course_title", "Untitled Course")
    module = config.get("module_title", "Untitled Module")

    data = []
    for lesson in lessons:
        row = {
            "Course": course,
            "Module": module,
            "Lesson": lesson,
            "Topic": f"Auto-generated topic for {lesson}"
        }
        data.append(row)

    df = pd.DataFrame(data)
    out_dir = "output/kep_extractor"
    os.makedirs(out_dir, exist_ok=True)
    filename = f"{out_dir}/kep_output_20250322_143513.csv"
    df.to_csv(filename, index=False)

    return {
        "status": "✅ Success",
        "outputs": [filename]
    }
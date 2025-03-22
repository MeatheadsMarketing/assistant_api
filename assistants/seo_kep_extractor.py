# assistants/seo_kep_extractor.py

from core.kep_processor import extract_kep

def run(config):
    """
    Trigger KEP extraction using config from Streamlit or API
    """
    course_title = config.get("course_title", "")
    module_title = config.get("module_title", "")
    lesson_list = config.get("lesson_titles", [])
    assistant_name = config.get("assistant_name", "SEO_Optimization_Assistant")

    print(f"🧠 Running KEP for: {course_title} > {module_title}")
    return extract_kep(course_title, module_title, lesson_list, assistant_name)

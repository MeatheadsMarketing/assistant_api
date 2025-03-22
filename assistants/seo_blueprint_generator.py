# assistants/seo_blueprint_generator.py

from core.blueprint_generator import generate_blueprint_from_csv

def run(config):
    """
    Trigger blueprint generation from a KEP CSV
    """
    csv_path = config.get("uploaded_csv")
    assistant_name = config.get("assistant_name", "SEO_Optimization_Assistant")
    output_dir_base = config.get("output_dir", "outputs")

    if not csv_path:
        raise ValueError("Missing CSV path in config for blueprint generator.")

    print(f"📐 Generating blueprint for: {csv_path}")
    return generate_blueprint_from_csv(csv_path, assistant_name, output_dir_base)

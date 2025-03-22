def run_assistant(config):
    task_type = config.get("task_type")

    if task_type == "web_scraper":
        from assistants.web_scraper import run_web_scraper
        return run_web_scraper(config)

    elif task_type == "api_fetcher":
        from assistants.api_fetcher import run_api_fetcher
        return run_api_fetcher(config)

    else:
        return f"❌ Unsupported task_type: {task_type}"

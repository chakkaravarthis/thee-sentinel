import json, os
 
CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/project_config.json")
 
def load_config(project: str) -> dict:
    try:
        with open(CONFIG_PATH) as f:
            configs = json.load(f)
        return configs.get(project, configs.get("default", {}))
    except Exception:
        return {}

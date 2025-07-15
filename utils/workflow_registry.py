import json
import os
from datetime import datetime

REGISTRY_PATH = "./output_file/workflow_registry.json"

def save_workflow_arn(name, arn, user_query, invoke_url):
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)

    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[name] = {
        "arn": arn,
        "user_query": user_query,
        "invoke_url": invoke_url,
        "timestamp": datetime.now().isoformat()
    }

    with open(REGISTRY_PATH, "w") as f:
        json.dump(data, f, indent=2)

import json
import os
from datetime import datetime, timezone
from config import AUDIT_LOG_PATH


def load_log() -> list[dict]:
    if not os.path.exists(AUDIT_LOG_PATH):
        return []

    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def write_log(entry: dict) -> None:
    logs = load_log()

    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    logs.append(entry)

    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=2)
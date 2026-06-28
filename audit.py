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


def save_log(logs: list[dict]) -> None:
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)

    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=2)


def write_log(entry: dict) -> None:
    logs = load_log()

    entry["timestamp"] = datetime.now(timezone.utc).isoformat()
    logs.append(entry)

    save_log(logs)


def update_submission_status(content_id: str, status: str, appeal_reasoning: str | None = None) -> bool:
    logs = load_log()

    updated = False

    for entry in logs:
        if entry.get("event_type") == "submission" and entry.get("content_id") == content_id:
            entry["status"] = status

            if appeal_reasoning:
                entry["appeal_reasoning"] = appeal_reasoning

            updated = True

    if updated:
        save_log(logs)

    return updated
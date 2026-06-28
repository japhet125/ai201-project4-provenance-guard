from audit import load_log, write_log, update_submission_status


def submit_appeal(content_id: str, creator_reasoning: str) -> dict:
    logs = load_log()

    matching_submission = None

    for entry in logs:
        if (
            entry.get("event_type") == "submission"
            and entry.get("content_id") == content_id
        ):
            matching_submission = entry

    if not matching_submission:
        return {
            "found": False,
            "message": "No submission found with that content_id."
        }

    previous_status = matching_submission.get("status", "classified")

    update_submission_status(
        content_id=content_id,
        status="under_review",
        appeal_reasoning=creator_reasoning
    )

    appeal_entry = {
        "event_type": "appeal",
        "content_id": content_id,
        "creator_reasoning": creator_reasoning,
        "previous_status": previous_status,
        "new_status": "under_review"
    }

    write_log(appeal_entry)

    return {
        "found": True,
        "content_id": content_id,
        "status": "under_review",
        "message": "Appeal received and marked for review."
    }
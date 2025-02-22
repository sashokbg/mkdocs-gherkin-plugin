def format_status(status: str):
    if status.lower() == "passed":
        return "✔"

    if status.lower() == "failed":
        return "❌"

    if status.lower() == "skipped":
        return "⏩"

    if status.lower() == "undefined":
        return "❓"

    return status

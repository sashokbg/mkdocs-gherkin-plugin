def format_status(status):
    if status == "PASSED" or status == "PASSED":
        return "✔"

    if status == "FAILED" or status == "FAILED":
        return "✖"

    if status == "SKIPPED" or status == "SKIPPED":
        return "Skipped"

    if status == "UNDEFINED" or status == "UNDEFINED":
        return "❔"

    return status

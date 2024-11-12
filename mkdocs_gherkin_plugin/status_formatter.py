from messages import Status

def format_status(status):
    if status == Status.passed.value or status == Status.passed:
        return "✔"

    if status == Status.failed.value or status == Status.failed:
        return "✖"

    if status == Status.skipped.value or status == Status.skipped:
        return "Skipped"

    if status == Status.undefined.value or status == Status.undefined:
        return "❔"

    return status

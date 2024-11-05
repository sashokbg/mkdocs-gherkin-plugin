from pathlib import Path
from typing import List

from messages import Status

from .gherkin_step import GherkinStep


class GherkinTestCase():

    def __init__(self, id, pickle_id):
        self.uri = None
        self.line = -1
        self.test_case_started_id = None
        self.id = id
        self.pickle_id = pickle_id
        self.steps: List[GherkinStep] = []

    def set_test_case_started_id(self, id):
        self.test_case_started_id = id

    def add_step(self, step: GherkinStep):
        self.steps.append(step)

    def set_line(self, line):
        self.line = line

    def status(self):
        all_skipped = True

        for step in self.steps:
            if step.result != Status.skipped:
                all_skipped = False
            if step.result == Status.failed:
                return Status.failed

        if all_skipped:
            return Status.skipped

        return Status.passed

    def matches_uri(self, other: Path):
        return Path(self.uri).resolve() == other.resolve()

    def set_uri(self, uri):
        self.uri = uri

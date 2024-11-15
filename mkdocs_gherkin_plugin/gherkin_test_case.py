from pathlib import Path
from typing import List

from messages import Status, Attachment

from .gherkin_step import GherkinStep


class GherkinTestCase():

    def __init__(self, id, pickle_id, steps: List[GherkinStep]):
        self.uri = None
        self.line = -1
        self.test_case_started_id = None
        self.id = id
        self.pickle_id = pickle_id
        self.steps: List[GherkinStep] = steps
        self.name = ""

    def get_step_by_definition_id(self, id):
        for step in self.steps:
            if step.id == id:
                return step
        return None

    def get_step_by_test_step_id(self, id):
        for step in self.steps:
            if id == step.test_step_id:
                return step

    def add_test_step_finished(self, test_step_finished):
        step = self.get_step_by_test_step_id(test_step_finished['testStepId'])
        if step:
            step.set_status(Status[test_step_finished['testStepResult']['status'].lower()])

    def add_pickle_step(self, pickle_step, ast_nodes, pickle):
        step = self.get_step_by_pickle_step_id(pickle_step.id)

        if step:
            step.set_ast_node_ids(pickle_step.ast_node_ids)
            step.set_text(pickle_step.text)

            for ast_node in ast_nodes:
                step.add_line(ast_node['location']['line'])
            step.set_pickle_uri(pickle.uri)

    def add_step_attachment(self, test_step_attachment: Attachment):
        step = self.get_step_by_test_step_id(test_step_attachment.test_step_id)

        if step:
            step.add_attachment(test_step_attachment)

    def get_step_by_pickle_step_id(self, id) -> GherkinStep:
        for step in self.steps:
            if id == step.pickle_step_id:
                return step

    def set_test_case_started_id(self, id):
        self.test_case_started_id = id

    def add_test_case_step(self, test_case_step):
        step = self.get_step_by_definition_id(test_case_step.step_definition_ids[0])
        step.set_test_step_id(test_case_step.id)
        step.set_pickle_step_id(test_case_step.pickle_step_id)

    def set_line(self, line):
        self.line = line

    def status(self):
        all_skipped = True
        all_undefined = True
        has_failed = False

        if not len(self.steps):
            return Status.skipped

        for step in self.steps:
            if step.status() != Status.skipped:
                all_skipped = False
            if step.status() != Status.undefined:
                all_undefined = False
            if step.status() == Status.failed:
                has_failed = True

        if all_skipped:
            result = Status.skipped
        elif all_undefined:
            result = Status.undefined
        elif has_failed:
            result = Status.failed
        else:
            result = Status.passed

        return result

    def matches_uri(self, other: Path):
        return Path(self.uri).resolve() == other.resolve()

    def set_uri(self, uri):
        self.uri = uri

    def set_name(self, name):
        self.name = name

    def __str__(self):
        return f"GherkinTestCase[id={self.id}, name={self.name}]"

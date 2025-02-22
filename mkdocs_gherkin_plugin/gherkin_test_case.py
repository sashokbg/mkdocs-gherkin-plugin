import logging
from pathlib import Path
from typing import List

from .gherkin_step import GherkinStep

log = logging.getLogger(f"mkdocs.plugins.{__name__}")

class GherkinTestCase:

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
            step.set_status(test_step_finished['testStepResult']['status'].lower())

    def add_pickle_step(self, pickle_step, ast_nodes, pickle):
        step = self.get_step_by_pickle_step_id(pickle_step.get("id"))

        if step:
            step.set_ast_node_ids(pickle_step.get("astNodeIds"))
            step.set_text(pickle_step.get("text"))

            for ast_node in ast_nodes:
                step.add_line(ast_node['location']['line'])
            step.set_pickle_uri(pickle.get("uri"))

    def add_step_attachment(self, test_step_attachment):
        step = self.get_step_by_test_step_id(test_step_attachment.get("testStepId"))

        if step:
            step.add_attachment(test_step_attachment)

    def get_step_by_pickle_step_id(self, step_id) -> GherkinStep:
        for step in self.steps:
            if step_id == step.pickle_step_id:
                return step

    def set_test_case_started_id(self, id):
        self.test_case_started_id = id

    def add_test_case_step(self, test_case_step):
        step = self.get_step_by_definition_id(test_case_step.get("stepDefinitionIds")[0])
        step.set_test_step_id(test_case_step.get("id"))
        step.set_pickle_step_id(test_case_step.get("pickleStepId"))

    def set_line(self, line):
        self.line = line

    def status(self):
        all_skipped = True
        all_undefined = True
        has_failed = False

        if not len(self.steps):
            return "SKIPPED"

        for step in self.steps:
            if step.status().lower() != "skipped":
                all_skipped = False
            if step.status().lower() != "undefined":
                all_undefined = False
            if step.status().lower() == "failed":
                has_failed = True

        if all_skipped:
            result = "skipped"
        elif all_undefined:
            result = "undefined"
        elif has_failed:
            result = "failed"
        else:
            result = "passed"

        return result

    def matches_uri(self, doc_page_path: Path, tests_root_path: str):
        path = Path(tests_root_path) / Path(self.uri)
        test_case_absolute_url = path.resolve()
        doc_page_absolute_url = doc_page_path.resolve()

        # log.info("MATCHING TEST-PAGE %s AND %s", test_case_absolute_url, doc_page_absolute_url)
        return test_case_absolute_url == doc_page_absolute_url

    def set_uri(self, uri):
        self.uri = uri

    def set_name(self, name):
        self.name = name

    def __str__(self):
        return f"GherkinTestCase[id={self.id}, name={self.name}, uri={self.uri}]"

from typing import List

from messages import StepDefinition, TestStep, TestStepFinished, PickleStep, Pickle, TestCase, TestCaseStarted

from .gherkin_step import GherkinStep
from .gherkin_test_case import GherkinTestCase


class GherkinResults():
    def __init__(self):
        self.steps: List[GherkinStep] = []
        self.test_cases: List[GherkinTestCase] = []

    def add_test_case(self, test_case: TestCase):
        self.test_cases.append(GherkinTestCase(id=test_case.id, pickle_id=test_case.pickle_id))

    def get_step_by_definition_id(self, id):
        for step in self.steps:
            if step.id == id:
                return step
        return None

    def get_step_by_test_step_id(self, id):
        for step in self.steps:
            if step.test_step_id == id:
                return step

    def get_step_by_pickle_step_id(self, id) -> GherkinStep:
        for step in self.steps:
            if step.pickle_step_id == id:
                return step

    def add_pickle_step(self, pickle_step: PickleStep, ast_nodes, pickle: Pickle):
        step = self.get_step_by_pickle_step_id(pickle_step.id)
        step.set_ast_node_ids(pickle_step.ast_node_ids)
        step.set_text(pickle_step.text)
        step.set_line(ast_nodes[0]['location']['line'])
        step.set_pickle_uri(pickle.uri)

    def add_step(self, step_definition: StepDefinition):
        self.steps.append(GherkinStep(id=step_definition.id))

    def add_test_case_step(self, test_case_step: TestStep):
        if test_case_step.step_definition_ids:
            step = self.get_step_by_definition_id(test_case_step.step_definition_ids[0])
            step.set_test_step_id(test_case_step.id)
            step.set_pickle_step_id(test_case_step.pickle_step_id)

    def add_test_step_finished(self, test_step_finished: TestStepFinished):
        step = self.get_step_by_test_step_id(test_step_finished.test_step_id)
        if step:
            step.set_result(test_step_finished.test_step_result)
            test_case = self.get_test_case_by_started_id(test_step_finished.test_case_started_id)
            test_case.add_step(step)

    def get_test_case_by_id(self, test_case_id):
        for test_case in self.test_cases:
            if test_case.id == test_case_id:
                return test_case

    def get_test_case_by_pickle_id(self, pickle_id):
        for test_case in self.test_cases:
            if test_case.pickle_id == pickle_id:
                return test_case

    def add_test_case_pickle(self, pickle: Pickle, ast_node):
        test_case = self.get_test_case_by_pickle_id(pickle.id)
        test_case.set_line(ast_node[0]['location']['line'])
        test_case.set_uri(pickle.uri)

    def add_test_case_start(self, test_case_started: TestCaseStarted):
        test_case = self.get_test_case_by_id(test_case_started.test_case_id)
        test_case.set_test_case_started_id(test_case_started.id)

    def get_test_case_by_started_id(self, test_case_started_id):
        for test_case in self.test_cases:
            if test_case.test_case_started_id == test_case_started_id:
                return test_case

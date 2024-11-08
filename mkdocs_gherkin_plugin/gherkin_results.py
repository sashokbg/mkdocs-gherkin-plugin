from typing import List

from messages import StepDefinition, TestStep, TestStepFinished, PickleStep, Pickle, TestCase, TestCaseStarted, Attachment

from .gherkin_step import GherkinStep
from .gherkin_test_case import GherkinTestCase


class GherkinResults():
    def __init__(self):
        self.steps: List[StepDefinition] = []
        self.test_cases: List[GherkinTestCase] = []

    def add_step_definitions(self, step_definitions: List[StepDefinition]):
        for step_def in step_definitions:
            self.steps.append(GherkinStep(id=step_def.id))

    def add_test_case(self, test_case: TestCase):
        steps = []
        for step in self.steps:
            for test_case_step in test_case.test_steps:
                if test_case_step.step_definition_ids and len(test_case_step.step_definition_ids) and step.id in test_case_step.step_definition_ids:
                    steps.append(GherkinStep(step.id))

        case = GherkinTestCase(
            id=test_case.id,
            pickle_id=test_case.pickle_id,
            steps=steps
        )
        self.test_cases.append(case)

    def add_pickle_step(self, pickle_step: PickleStep, ast_nodes, pickle: Pickle):
        case = self.get_test_case_by_pickle_id(pickle.id)

        case.add_pickle_step(pickle_step, ast_nodes, pickle)


    # def add_step(self, step_definition: StepDefinition):
    #     self.steps.append(GherkinStep(id=step_definition.id))
    #
    def add_test_case_step(self, test_case_id, test_case_step: TestStep):
        if test_case_step.step_definition_ids:
            case = self.get_test_case_by_id(test_case_id)

            case.add_test_case_step(test_case_step)

    def add_test_step_finished(self, test_step_finished):
        case = self.get_test_case_by_started_id(test_step_finished['testCaseStartedId'])

        case.add_test_step_finished(test_step_finished)

    def add_test_step_attachment(self, test_step_attachment: Attachment):
        case = self.get_test_case_by_started_id(test_step_attachment.test_case_started_id)
        case.add_step_attachment(test_step_attachment)

    def get_test_case_by_id(self, test_case_id) -> GherkinTestCase:
        for test_case in self.test_cases:
            if test_case.id == test_case_id:
                return test_case

    def get_test_case_by_pickle_id(self, pickle_id) -> GherkinTestCase:
        for test_case in self.test_cases:
            if test_case.pickle_id == pickle_id:
                return test_case

    def add_test_case_pickle(self, pickle: Pickle, ast_node):
        test_case = self.get_test_case_by_pickle_id(pickle.id)
        test_case.set_line(ast_node[0]['location']['line'])
        test_case.set_uri(pickle.uri)
        test_case.set_name(pickle.name)

    def add_test_case_start(self, test_case_started: TestCaseStarted):
        test_case = self.get_test_case_by_id(test_case_started.test_case_id)
        test_case.set_test_case_started_id(test_case_started.id)

    def get_test_case_by_started_id(self, test_case_started_id) -> GherkinTestCase:
        for test_case in self.test_cases:
            if test_case.test_case_started_id == test_case_started_id:
                return test_case

import json
import logging
import pathlib

from messages import StepDefinition, PickleStep, TestCase, TestCaseStarted, Pickle
from mkdocs import plugins

from .gherkin_results import GherkinResults

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class GherkinPlugin(plugins.BasePlugin):

    def __init__(self, *args, **kwargs):
        self.results: GherkinResults = None
        self.process_document("gherkin_messages.ndjson")

    def on_page_markdown(self, markdown, page, config, files):
        lines = markdown.splitlines()

        docfile_path = pathlib.Path(page.file.abs_src_path)

        for test_case in self.results.test_cases:
            if test_case.matches_uri(docfile_path):
                for step in test_case.steps:
                        for line in step.lines:
                            # if str(step.result['status']) not in lines[line - 1]:
                            lines[line - 1] += f" {step.result['status']}"


                # if str(test_case.status()) not in lines[test_case.line - 1]:
                lines[test_case.line - 1] += f" {test_case.status()}"

        result = ""

        for line in lines:
            result += line + "\n"

        return result

    def search(self, obj, key, value, results):
        if isinstance(obj, dict):
            # Check if the key exists at the current level
            if key in obj and obj[key] == value:
                results.append(obj)
            else:
                # Recursively search each key-value pair
                for v in obj.values():
                    self.search(v, key, value, results)
        elif isinstance(obj, list):
            # Iterate through each item in a list
            for item in obj:
                self.search(item, key, value, results)

    def process_document(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            ndjson_objects = [json.loads(line) for line in file if line.strip()]

        step_definitions = []
        test_steps, test_cases = [], []
        pickles, finished_test_cases, started_test_cases, started_steps, finished_steps = [], [], [], [], []
        gherkin_document = None

        log.info("STARTING GHERKIN PLUGIN")

        for obj in ndjson_objects:
            if 'pickle' in obj:
                pickles.append(Pickle.model_validate(obj['pickle']))
            if 'stepDefinition' in obj:
                step_definitions.append(StepDefinition.model_validate(obj['stepDefinition']))
            if 'testCase' in obj:
                test_cases.append(TestCase.model_validate(obj['testCase']))
            if 'testCaseFinished' in obj:
                finished_test_cases.append(obj['testCaseFinished'])
            if 'testCaseStarted' in obj:
                started_test_cases.append(TestCaseStarted.model_validate(obj['testCaseStarted']))
            if 'testStepStarted' in obj:
                started_steps.append(obj['testStepStarted'])
            if 'testStepFinished' in obj:
                # TestStepFinished.model_config["extra"] = "allow"
                # TestStepResult.model_config["extra"] = "allow"
                # ExceptionMessage.model_config["extra"] = "allow"

                # finished_steps.append(TestStepFinished.model_validate(obj['testStepFinished']))
                finished_steps.append(obj['testStepFinished'])
            if 'gherkinDocument' in obj:
                gherkin_document = obj['gherkinDocument']

        results = GherkinResults()

        # for step_definition in step_definitions.values():
        #     results.add_step(step_definition)

        for test_case in test_cases:
            results.add_test_case(test_case, step_definitions)

            for test_step in test_case.test_steps:
                results.add_test_case_step(test_case.id, test_step)

        for test_case_started in started_test_cases:
            results.add_test_case_start(test_case_started)

        for pickle in pickles:
            pickle_ast_nodes = []
            for astNodeId in pickle.ast_node_ids:
                self.search(gherkin_document, "id", astNodeId, pickle_ast_nodes)
            results.add_test_case_pickle(pickle, pickle_ast_nodes)

            for step in pickle.steps:
                ast_nodes = []
                for astNodeId in step.ast_node_ids:
                    self.search(gherkin_document, "id", astNodeId, ast_nodes)

                results.add_pickle_step(PickleStep.model_validate(step), ast_nodes, pickle)

        for finished_step in finished_steps:
            results.add_test_step_finished(finished_step)

        self.results = results

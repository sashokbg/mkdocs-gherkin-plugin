import json
import logging
import pathlib

from messages import StepDefinition, PickleStep, TestCase, TestCaseStarted, Pickle, Attachment
from mkdocs import plugins, config
from mkdocs.config.defaults import MkDocsConfig

from .gherkin_results import GherkinResults

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class GherkinPluginConfig(config.base.Config):
    show_attachments = config.config_options.Type(bool, default=True)
    messages_path = config.config_options.Type(str, default="gherkin_messages.ndjson")


class GherkinPlugin(plugins.BasePlugin[GherkinPluginConfig]):

    def __init__(self, *args, **kwargs):
        self.results: GherkinResults = None

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        message_file = self.config['messages_path']
        self.process_document(message_file)


    def on_page_markdown(self, markdown, page, config, files):
        lines = markdown.splitlines()

        docfile_path = pathlib.Path(page.file.abs_src_path)

        for test_case in self.results.test_cases:
            if test_case.matches_uri(docfile_path):
                for n, line in enumerate(lines):
                    if "<" in line:
                        lines[n] = lines[n].replace("<", "&lt;")

                for step in test_case.steps:
                    for line in step.lines:
                        lines[line - 1] += f" {step.result()}"

                lines[test_case.line - 1] += f" {test_case.status()}"

        if self.config['show_attachments']:
            self.add_attachments(docfile_path, lines)

        result = ""

        for line in lines:
            result += line + "\n"

        return result

    def add_attachments(self, docfile_path, lines):
        for test_case in self.results.test_cases:
            if test_case.matches_uri(docfile_path):
                for step in test_case.steps:
                    for attachment in step.attachments:
                        lines[step.lines[0]-1] += f"""
??? Screenshot
    ![{attachment.file_name}](data:{attachment.media_type};BASE64,{attachment.body})"""

    def search(self, obj, key, value, results):
        if isinstance(obj, dict):
            if key in obj and obj[key] == value:
                results.append(obj)
            else:
                for v in obj.values():
                    self.search(v, key, value, results)
        elif isinstance(obj, list):
            for item in obj:
                self.search(item, key, value, results)

    def process_document(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            ndjson_objects = [json.loads(line) for line in file if line.strip()]

        step_definitions = []
        test_steps, test_cases = [], []
        pickles, finished_test_cases, started_test_cases, started_steps, finished_steps = [], [], [], [], []
        gherkin_documents = []
        attachments = []

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
                finished_steps.append(obj['testStepFinished'])
            if 'gherkinDocument' in obj:
                gherkin_documents.append(obj['gherkinDocument'])
            if 'attachment' in obj:
                attachments.append(Attachment.model_validate(obj['attachment']))

        results = GherkinResults()

        results.add_step_definitions(step_definitions)

        for test_case in test_cases:
            results.add_test_case(test_case)

            for test_step in test_case.test_steps:
                results.add_test_case_step(test_case.id, test_step)

        for test_case_started in started_test_cases:
            results.add_test_case_start(test_case_started)

        for pickle in pickles:
            pickle_ast_nodes = []
            for astNodeId in pickle.ast_node_ids:
                for gherkin_document in gherkin_documents:
                    self.search(gherkin_document, "id", astNodeId, pickle_ast_nodes)

            if not len(pickle_ast_nodes):
                break

            results.add_test_case_pickle(pickle, pickle_ast_nodes)

            for pickle_step in pickle.steps:
                ast_nodes = []
                for astNodeId in pickle_step.ast_node_ids:
                    for gherkin_document in gherkin_documents:
                        self.search(gherkin_document, "id", astNodeId, ast_nodes)

                results.add_pickle_step(PickleStep.model_validate(pickle_step), ast_nodes, pickle)

        for finished_step in finished_steps:
            results.add_test_step_finished(finished_step)

        for attachment in attachments:
            results.add_test_step_attachment(attachment)

        self.results = results

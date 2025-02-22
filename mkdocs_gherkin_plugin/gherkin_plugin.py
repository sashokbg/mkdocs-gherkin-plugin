import json
import logging
import os.path
import pathlib

from mkdocs import plugins, config
from mkdocs.config.defaults import MkDocsConfig

from .gherkin_results import GherkinResults
from .status_formatter import format_status

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class GherkinPluginConfig(config.base.Config):
    show_attachments = config.config_options.Type(bool, default=True)
    show_results = config.config_options.Type(bool, default=True)
    messages_path = config.config_options.Type(str, default="gherkin_messages.ndjson")
    tests_root_path = config.config_options.Type(str)


class GherkinPlugin(plugins.BasePlugin[GherkinPluginConfig]):

    def __init__(self, *args, **kwargs):
        log.info("Loading Gherkin plugin")
        self.results: GherkinResults | None = None

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        message_file = self.config['messages_path']
        tests_path = self.config['tests_root_path']

        is_ok = True
        if not os.path.isfile(message_file) or not os.path.exists(message_file):
            is_ok = False
            log.warning("No gherkin results found in %s. Skipping plugin execution.", message_file)

        if not os.path.isdir(tests_path) or not os.path.exists(tests_path):
            is_ok = False
            log.warning(
                "Tests path not existing. Please set it to the location dir of your e2e tests. Skipping plugin execution")

        if is_ok:
            self.process_document(message_file)

    def on_page_markdown(self, markdown, page, config, files):
        if self.results is None:
            return

        message_file = self.config['messages_path']
        if not os.path.isfile(message_file) or not os.path.exists(message_file):
            return markdown

        lines = markdown.splitlines()

        docfile_path = pathlib.Path(page.file.abs_src_path)

        for test_case in self.results.test_cases:
            if test_case.matches_uri(docfile_path, self.config["tests_root_path"]):
                for n, line in enumerate(lines):
                    if "<" in line:
                        lines[n] = lines[n].replace("<", "&lt;")

                if self.config['show_results']:
                    for step in test_case.steps:
                        for line in step.lines:
                            lines[line - 1] += f" {format_status(step.status())}"

                    lines[test_case.line - 1] += f" {format_status(test_case.status())}"

        if self.config['show_attachments']:
            self.add_attachments(docfile_path, lines)

        result = ""

        for line in lines:
            result += line + "\n"

        return result

    def add_attachments(self, docfile_path, lines):
        for test_case in self.results.test_cases:
            if test_case.matches_uri(docfile_path, self.config["tests_root_path"]):
                for step in test_case.steps:
                    for attachment in step.attachments:
                        lines[step.lines[0] - 1] += f"""
??? Screenshot
    ![{attachment.get("fileName")}](data:{attachment.get("mediaType")};BASE64,{attachment.get("body")})"""

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

        for obj in ndjson_objects:
            if 'pickle' in obj:
                pickles.append(obj['pickle'])
            if 'stepDefinition' in obj:
                step_definitions.append(obj['stepDefinition'])
            if 'testCase' in obj:
                test_cases.append(obj['testCase'])
            if 'testCaseFinished' in obj:
                finished_test_cases.append(obj['testCaseFinished'])
            if 'testCaseStarted' in obj:
                started_test_cases.append(obj['testCaseStarted'])
            if 'testStepStarted' in obj:
                started_steps.append(obj['testStepStarted'])
            if 'testStepFinished' in obj:
                finished_steps.append(obj['testStepFinished'])
            if 'gherkinDocument' in obj:
                gherkin_documents.append(obj['gherkinDocument'])
            if 'attachment' in obj:
                attachments.append(obj['attachment'])

        results = GherkinResults()

        results.add_step_definitions(step_definitions)

        for test_case in test_cases:
            results.add_test_case(test_case)

            for test_step in test_case.get("testSteps"):
                results.add_test_case_step(test_case.get("id"), test_step)

        for test_case_started in started_test_cases:
            results.add_test_case_start(test_case_started)

        for pickle in pickles:
            if not results.get_test_case_by_pickle_id(pickle.get("id")):
                log.warning("No test case found for pickle %s", pickle.get("id"))
                continue

            pickle_ast_nodes = []
            for astNodeId in pickle.get("astNodeIds"):
                for gherkin_document in gherkin_documents:
                    self.search(gherkin_document, "id", astNodeId, pickle_ast_nodes)

            if not len(pickle_ast_nodes):
                break

            results.add_test_case_pickle(pickle, pickle_ast_nodes)

            for pickle_step in pickle.get("steps"):
                ast_nodes = []
                for astNodeId in pickle_step.get("astNodeIds"):
                    for gherkin_document in gherkin_documents:
                        self.search(gherkin_document, "id", astNodeId, ast_nodes)

                results.add_pickle_step(pickle_step, ast_nodes, pickle)

        for finished_step in finished_steps:
            results.add_test_step_finished(finished_step)

        for attachment in attachments:
            results.add_test_step_attachment(attachment)

        self.results = results

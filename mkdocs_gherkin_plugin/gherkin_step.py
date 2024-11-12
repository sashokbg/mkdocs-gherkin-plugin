from pathlib import Path
from typing import List

from messages import Attachment
from .status_formatter import format_status


class GherkinStep():
    def __init__(self, id):
        self.uri = None
        self.ast_node_ids = None
        self.text = None
        self.id = id
        self.lines = []
        self._result = ""
        self.test_step_id = None
        self.pickle_step_id = None
        self.attachments: List[Attachment] = []

    def result(self):
        if not self._result:
            return None

        status = self._result['status']
        return format_status(status)


    def set_result(self, result):
        self._result = result

    def add_line(self, line):
        if line not in self.lines:
            self.lines.append(line)

    def set_test_step_id(self, id):
        self.test_step_id = id

    def set_pickle_step_id(self, id):
        self.pickle_step_id = id

    def set_ast_node_ids(self, ast_node_ids):
        self.ast_node_ids = ast_node_ids

    def set_text(self, text):
        self.text = text

    def set_pickle_uri(self, uri):
        self.uri = uri

    def add_attachment(self, attachment: Attachment):
        self.attachments.append(attachment)

    def matches_uri(self, other: Path):
        return Path(self.uri).resolve() == other.resolve()

    def __str__(self):
        return f"step[id={self.id}, result={self._result}, text={self.text}, lines={self.lines}, attachments={self.attachments}]"

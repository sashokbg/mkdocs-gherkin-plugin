from pathlib import Path


class GherkinStep():
    def __init__(self, id):
        self.uri = None
        self.ast_node_ids = None
        self.text = None
        self.id = id
        self.line = -1
        self.result = ""
        self.test_step_id = None
        self.pickle_step_id = None

    def set_result(self, result):
        self.result = result

    def set_line(self, line):
        self.line = line

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

    def matches_uri(self, other: Path):
        return Path(self.uri).resolve() == other.resolve()

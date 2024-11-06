from pathlib import Path


class GherkinStep():
    def __init__(self, id):
        self.uri = None
        self.ast_node_ids = None
        self.text = None
        self.id = id
        self.lines = []
        self.result = ""
        self.test_step_ids = []
        self.pickle_step_ids = []

    def set_result(self, result):
        self.result = result

    def add_line(self, line):
        self.lines.append(line)

    def add_test_step_id(self, id):
        self.test_step_ids.append(id)

    def add_pickle_step_id(self, id):
        self.pickle_step_ids.append(id)

    def set_ast_node_ids(self, ast_node_ids):
        self.ast_node_ids = ast_node_ids

    def set_text(self, text):
        self.text = text

    def set_pickle_uri(self, uri):
        self.uri = uri

    def matches_uri(self, other: Path):
        return Path(self.uri).resolve() == other.resolve()

    def __str__(self):
        return f"step[id={self.id}, result={self.result}]"

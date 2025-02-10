from mkdocs_gherkin_plugin.gherkin_step import GherkinStep
from mkdocs_gherkin_plugin.gherkin_test_case import GherkinTestCase

def init_test_case(*statuses):
    steps = []

    for status in statuses:
        step = GherkinStep("step")
        step.set_status(status)
        steps.append(step)

    test_case = GherkinTestCase("1", "1", steps)
    return test_case


def test_case_status():
    test_case = init_test_case("PASSED")

    assert test_case.status() == "PASSED"

def test_case_fail_when_one_step_failed():
    test_case = init_test_case("PASSED", "FAILED")

    assert test_case.status() == "FAILED"

def test_case_skipped_when_all_step_skipped():
    test_case = init_test_case("SKIPPED", "SKIPPED", "SKIPPED")

    assert test_case.status() == "SKIPPED"

def test_case_failed_when_at_least_one_failed():
    test_case = init_test_case("PASSED", "FAILED", "SKIPPED")

    assert test_case.status() == "FAILED"

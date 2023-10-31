import unittest

from rcmt.task import registry
from rcmt.validate import validate


class ValidateTest(unittest.TestCase):
    def setUp(self):
        registry.tasks = []

    def test_validate__valid(self):
        paths = (
            "tests/fixtures/test_validate/valid/task_one.py",
            "tests/fixtures/test_validate/valid/task_two.py",
        )
        result = validate(task_file_paths=paths)

        self.assertTrue(result, "Should return True if all Tasks are valid")

    def test_validate__invalid(self):
        paths = (
            "tests/fixtures/test_validate/invalid/task_one.py",
            "tests/fixtures/test_validate/invalid/task_two.py",
        )
        result = validate(task_file_paths=paths)

        self.assertFalse(result, "Should return False if validation failed")

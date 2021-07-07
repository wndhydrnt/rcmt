import unittest

from rcmt.action import DeleteKeys


class DeleteKeysTest(unittest.TestCase):
    def test_process(self):
        data = {"foo": "bar", "level1": {"level2": {"level3": "foo"}}}
        key_to_delete = {"level1": {"level2": {"level3": None}}}
        result = DeleteKeys.process_recursive(key_to_delete, data)
        self.assertDictEqual({"foo": "bar", "level1": {"level2": {}}}, result)

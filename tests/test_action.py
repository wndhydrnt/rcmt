import unittest
from unittest import mock

from rcmt import encoding
from rcmt.action import DeleteKey, Exec, exec_factory


class ExecTest(unittest.TestCase):
    @mock.patch("subprocess.run")
    def test_exec(self, subprocess_run: mock.MagicMock):
        completed_process = mock.Mock(returncode=1, stderr=b"stderr", stdout=b"stdout")
        subprocess_run.return_value = completed_process
        ex = Exec(exec_path="/tmp/foo", timeout=120)
        with self.assertRaises(RuntimeError) as e:
            ex.apply("anyfile", {})
        self.assertEqual(
            """Exec action call to /tmp/foo failed.
    stdout: stdout
    stderr: stderr""",
            str(e.exception),
        )


class DeleteKeysTest(unittest.TestCase):
    def test_process(self):
        data = {"foo": "bar", "level1": {"level2": {"level3": "foo"}}}
        key_to_delete = ["level1", "level2", "level3"]
        result = DeleteKey.process_recursive(key_to_delete, data)
        self.assertDictEqual({"foo": "bar", "level1": {"level2": {}}}, result)

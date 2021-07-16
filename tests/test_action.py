import unittest
from unittest import mock

from rcmt.action import DeleteKey, Exec


class ExecTest(unittest.TestCase):
    @mock.patch("subprocess.run")
    @mock.patch("glob.iglob")
    def test_exec(self, glob_iglob: mock.MagicMock, subprocess_run: mock.MagicMock):
        completed_process = mock.Mock(returncode=1, stderr=b"stderr", stdout=b"stdout")
        subprocess_run.return_value = completed_process
        glob_iglob.return_value = ["/repo-checkout/afile"]
        ex = Exec(exec_path="/tmp/foo", selector="afile", timeout=120)
        with self.assertRaises(RuntimeError) as e:
            ex.apply("/repo-checkout", {})
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

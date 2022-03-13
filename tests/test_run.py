import unittest

from rcmt.run import read


class ReadRunTest(unittest.TestCase):
    def test_read(self):
        r = read("tests/fixtures/test_run/ReadRunTest/test_read/run.py")
        for fp in r.file_proxies:
            self.assertEqual("tests/fixtures/test_run/ReadRunTest/test_read", fp.path)

    def test_read_invalid_type(self):
        with self.assertRaises(RuntimeError) as e:
            read("tests/fixtures/test_run/ReadRunTest/test_read_invalid_type/run.py")

        self.assertEqual(
            "Run file tests/fixtures/test_run/ReadRunTest/test_read_invalid_type/run.py defines variable 'run' but is not of type Run",
            str(e.exception),
        )

    def test_read_run_var_not_exists(self):
        with self.assertRaises(RuntimeError) as e:
            read(
                "tests/fixtures/test_run/ReadRunTest/test_read_run_var_not_exists/run.py"
            )

        self.assertEqual(
            "Run file tests/fixtures/test_run/ReadRunTest/test_read_run_var_not_exists/run.py does not define variable 'run'",
            str(e.exception),
        )

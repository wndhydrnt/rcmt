import unittest

from rcmt.run import read, read_file


class ReadTest(unittest.TestCase):
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


class ReadFileTest(unittest.TestCase):
    def test_json(self):
        r = read_file("tests/fixtures/test_run/ReadFileTest/test_json/run.json")

        self.assertEqual("test-json", r.name)

    def test_yaml(self):
        r = read_file("tests/fixtures/test_run/ReadFileTest/test_yaml/run.yaml")

        self.assertEqual("test-yaml", r.name)

    def test_py(self):
        r = read_file("tests/fixtures/test_run/ReadRunTest/test_read/run.py")

        self.assertEqual("unit-test", r.name)

    def test_unsupported(self):
        with self.assertRaises(RuntimeError):
            read_file("tests/fixtures/test_run/ReadFileTest/test_unsupported/run.txt")

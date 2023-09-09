import os.path
import tempfile
import unittest

from rcmt.action.semgrep import Semgrep

rules = """rules:
  - id: use-sys.exit
    pattern: exit($...X)
    message: Use sys.exit() instead of exit()
    languages:
      - python
    severity: INFO
    fix: sys.exit($...X)
"""


content_original = """def main():
    print("Hello from main()")
    exit(0)


if __name__ == "__main__":
    main()
"""

content_expected = """def main():
    print("Hello from main()")
    sys.exit(0)


if __name__ == "__main__":
    main()
"""


class SemgrepTest(unittest.TestCase):
    def test_apply__refactor(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "main.py")
            with open(path, "w+") as f:
                f.write(content_original)

            under_test = Semgrep(rules=rules, selector="main.py")
            under_test.apply(repo_path=d, tpl_data={})

            with open(path, mode="r") as f:
                content = f.read()

            self.assertEqual(content_expected, content)

    def test_apply__invalid_rules(self):
        rules = """rules:
  - id: use-sys.exit
    pattern: exit($...X)
    languages:
      - python
    severity: INFO
    fix: sys.exit($...X)
"""

        with tempfile.TemporaryDirectory() as d:
            under_test = Semgrep(rules=rules, selector="main.py")
            with self.assertRaises(RuntimeError) as e:
                under_test.apply(repo_path=d, tpl_data={})

            self.assertEqual(
                "semgrep raised an exception: invalid configuration file found (1 configs were invalid)",
                str(e.exception),
            )

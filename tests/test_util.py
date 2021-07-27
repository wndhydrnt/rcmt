import os
import tempfile
import unittest

from rcmt import util


class UtilTest(unittest.TestCase):
    def test_iglob(self):
        with tempfile.TemporaryDirectory() as dirname:
            test_file = os.path.join(dirname, "test.txt")
            with open(test_file, "w+") as f:
                f.write("test")

            result = list(util.iglob(dirname, "*.txt"))
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], test_file)

            sub_dir = os.path.join(dirname, "subdir")
            os.mkdir(sub_dir)
            with open(os.path.join(sub_dir, "subtext.txt"), "w+") as f:
                f.write("test")

            with self.assertRaises(RuntimeError) as ee:
                list(util.iglob(sub_dir, "../*.txt"))

            self.assertEqual(
                str(ee.exception), "Selector ../*.txt escapes root directory"
            )

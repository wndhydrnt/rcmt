# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import tempfile
import unittest
import unittest.mock

from rcmt import action, filter
from rcmt.config import Config
from rcmt.context import Context
from rcmt.git import Git
from rcmt.rcmt import Options
from rcmt.source import source
from rcmt.task import TaskWrapper, registry
from rcmt.verify import execute


class ExecuteTest(unittest.TestCase):
    def setUp(self) -> None:
        registry.task_path = None
        registry.tasks = []

    @unittest.mock.patch("rcmt.task.read")
    @unittest.mock.patch("rcmt.git.Git")
    def test_execute(self, git_class_mock, task_read_mock):
        task_read_mock.return_value = None

        opts = Options(cfg=Config())
        opts.task_paths = ["/tmp/run.py"]

        repository_mock = unittest.mock.Mock(spec=source.Repository)
        repository_mock.name = "rcmt"
        repository_mock.project = "wndhydrnt"
        repository_mock.source = "github.com"

        source_mock = unittest.mock.Mock(spec=source.Base)
        source_mock.create_from_name.return_value = repository_mock
        opts.sources["github.com"] = source_mock

        task = unittest.mock.Mock(spec=TaskWrapper)
        task.name = "local"
        task.filter.return_value = True
        registry.tasks.append(task)

        git_mock = unittest.mock.Mock(spec=Git)
        checkout_dir = tempfile.TemporaryDirectory()
        git_mock.prepare.return_value = (checkout_dir.name, False)
        git_class_mock.return_value = git_mock

        with open("/dev/null", "w") as f:
            execute(
                directory="/tmp/repository",
                opts=opts,
                out=f,
                repo_name="github.com/wndhydrnt/rcmt",
            )

        task.filter.assert_called()
        ctx = task.filter.call_args.kwargs["ctx"]
        self.assertIsInstance(ctx, Context)
        self.assertEqual(repository_mock, ctx.repo)
        task_read_mock.assert_called_with("/tmp/run.py")
        task.apply.assert_called_once_with(ctx=ctx)
        checkout_dir.cleanup()

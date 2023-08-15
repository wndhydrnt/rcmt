import unittest
import unittest.mock

from rcmt import Task, action, encoding, matcher
from rcmt.config import Config
from rcmt.git import Git
from rcmt.rcmt import Options
from rcmt.source import source
from rcmt.verify import execute


class ExecuteTest(unittest.TestCase):
    @unittest.mock.patch("rcmt.task.read")
    @unittest.mock.patch("rcmt.git.Git")
    def test_execute(self, git_class_mock, task_read_mock):
        opts = Options(cfg=Config())
        opts.task_paths = ["/tmp/run.py"]
        opts.encoding_registry = encoding.Registry()

        repository_mock = unittest.mock.Mock(spec=source.Repository)
        repository_mock.name = "rcmt"
        repository_mock.project = "wndhydrnt"
        repository_mock.source = "github.com"

        source_mock = unittest.mock.Mock(spec=source.Base)
        source_mock.create_from_name.return_value = repository_mock
        opts.sources["github.com"] = source_mock

        task = Task(name="local")
        matcher_mock = unittest.mock.Mock(spec=matcher.Base)
        matcher_mock.return_value = True
        task.add_matcher(matcher_mock)
        action_mock = unittest.mock.Mock(spec=action.Action)
        task.add_action(action_mock)
        task_read_mock.return_value = task

        git_mock = unittest.mock.Mock(spec=Git)
        checkout_dir = "/tmp/repository/github.com/wndhydrnt/rcmt"
        git_mock.prepare.return_value = (checkout_dir, False)
        git_class_mock.return_value = git_mock

        with open("/dev/null", "w") as f:
            execute(
                directory="/tmp/repository",
                opts=opts,
                out=f,
                repo_name="github.com/wndhydrnt/rcmt",
            )

        matcher_mock.assert_called_with(repository_mock)
        task_read_mock.assert_called_with("/tmp/run.py")
        action_mock.assert_called_once_with(
            checkout_dir,
            {
                "repo_source": "github.com",
                "repo_project": "wndhydrnt",
                "repo_name": "rcmt",
            },
        )

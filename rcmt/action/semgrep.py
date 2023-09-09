import os.path
import tempfile
from typing import Optional, Sequence, Union

from .. import util
from ..action import Action
from ..fs import FileProxy, read_file_or_str

try:
    import semgrep.run_scan
    from semgrep.error import SemgrepError
    from semgrep.metrics import MetricsState
    from semgrep.output import OutputFormat, OutputHandler, OutputSettings
    from semgrep.state import get_state
except ImportError:
    raise RuntimeError(
        "optional package semgrep not available - install via 'pip install rcmt[semgrep]'"
    )


class Semgrep(Action):
    def __init__(
        self,
        rules: Union[str, FileProxy],
        selector: str,
        exclude: Optional[Sequence[str]] = None,
        include: Optional[Sequence[str]] = None,
    ):
        self.exclude = exclude
        self.include = include
        self.rules = rules
        self.selector = selector

    def apply(self, repo_path: str, tpl_data: dict) -> None:
        semgrep_state = get_state()
        semgrep_state.metrics.configure(
            metrics_state=MetricsState.OFF, legacy_state=MetricsState.OFF
        )
        content = read_file_or_str(self.rules)
        with tempfile.TemporaryDirectory() as d:
            rules_file = os.path.join(d, "rules.yaml")
            with open(file=rules_file, mode="w+b") as f:
                f.write(content.encode("utf-8"))

            output_handler = OutputHandler(
                OutputSettings(output_format=OutputFormat.TEXT)
            )
            targets = util.iglob(root=repo_path, selector=self.selector)
            try:
                semgrep.run_scan.run_scan(
                    autofix=True,  # Always True, otherwise there is nothing to commit
                    configs=(f.name,),
                    dryrun=False,  # Always False, otherwise there is nothing to commit
                    exclude=self.exclude,
                    include=self.include,
                    lang=None,  # Always None, will be set via 'configs'
                    output_handler=output_handler,
                    pattern=None,  # Always None, will be set via 'configs'
                    target=tuple(targets),
                )
            except SemgrepError as e:
                raise RuntimeError(f"semgrep raised an exception: {str(e)}")

        return None

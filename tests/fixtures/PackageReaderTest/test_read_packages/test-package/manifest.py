from rcmt.action import Seed
from rcmt.package import Manifest

with Manifest(name="test-package") as manifest:
    manifest.add_action(Seed(content="", target="test.yaml"))

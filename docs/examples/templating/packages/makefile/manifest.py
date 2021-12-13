from rcmt.package import Manifest
from rcmt.package.action import Seed

with Manifest(name="makefile") as manifest:
    manifest.add_action(Seed(target="Makefile", source=manifest.load_file("Makefile")))

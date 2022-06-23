from rcmt.action import Seed
from rcmt.package import Manifest

with Manifest(name="makefile") as manifest:
    manifest.add_action(Seed(content=manifest.load_file("Makefile"), target="Makefile"))

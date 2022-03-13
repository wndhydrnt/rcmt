from rcmt.package import Manifest
from rcmt.package.action import Own

with Manifest(name="flake8") as manifest:
    manifest.add_action(Own(content=manifest.load_file(".flake8"), target=".flake8"))

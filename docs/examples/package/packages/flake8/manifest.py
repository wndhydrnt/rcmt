from rcmt.action import Own
from rcmt.package import Manifest

with Manifest(name="flake8") as manifest:
    manifest.add_action(Own(content=manifest.load_file(".flake8"), target=".flake8"))

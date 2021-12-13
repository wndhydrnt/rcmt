from rcmt.package import Manifest
from rcmt.package.action import Own

# This name identifies the package.
# rcmt errors if two packages share the same name.
with Manifest(name="flake8") as manifest:
    # Actions tell rcmt what to do and how.
    manifest.add_action(
        # The action to apply. The "own" action lets rcmt
        # take ownership of the file.
        # rcmt resets the file if somebody changes it in a repository.
        Own(
            # Path to the source file rcmt should put in a repository.
            # This path is relative to the manifest.py file.
            source=".flake8",
            # Path to the target where rcmt writes the content of source.
            # This is relative to the root path of a repository.
            target=".flake8",
        )
    )

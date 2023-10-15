# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt.action import Seed
from rcmt.package import Manifest

with Manifest(name="test-package") as manifest:
    manifest.add_action(Seed(content="", target="test.yaml"))

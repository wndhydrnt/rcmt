# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt import Task
from rcmt.action import Own

with Task("unit-test") as task:
    task.add_action(Own(content="This is a unit test", target="test.txt"))

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt import Task, register_task

d = {}
print(d["unknown"])


class UnitTestException(Task):
    name = "unit-test-exception"


register_task(UnitTestException())

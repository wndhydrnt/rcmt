# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt import Context, Task, register_task
from rcmt.action import own


class UnitTest(Task):
    name = "unit-test"
    enabled = False

    def apply(self, ctx: Context) -> None:
        own(ctx=ctx, content="This is a unit test", target="test.txt")


register_task(UnitTest())

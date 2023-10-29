# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt import Task, context, register_task
from rcmt.action import own


class UniTest(Task):
    name = "unit-test"

    def apply(self, ctx: context.Context) -> None:
        own(ctx=ctx, content=self.load_file("test.txt"), target="test.txt")


register_task(UniTest())

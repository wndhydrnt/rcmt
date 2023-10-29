# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt import Task, context, register_task
from rcmt.action import own

d = {}
v = d["key"]


class UniTest(Task):
    name = "unittest"

    def apply(self, ctx: context.Context) -> None:
        own(ctx=ctx, content="unittest", target="test.txt")


register_task(UniTest())

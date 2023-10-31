# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt import Context, Task, register_task


class TaskTwo(Task):
    # Invalid: Has the same name as the Task in task_one.py
    name = "task-one"

    def filter(self, ctx: Context) -> bool:
        return False

    def apply(self, ctx: Context) -> None:
        return None


register_task(TaskTwo())

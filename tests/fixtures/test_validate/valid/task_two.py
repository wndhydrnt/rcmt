from rcmt import Context, Task, register_task


class TaskTwo(Task):
    name = "task-two"

    def filter(self, ctx: Context) -> bool:
        return False

    def apply(self, ctx: Context) -> None:
        return None


register_task(TaskTwo())

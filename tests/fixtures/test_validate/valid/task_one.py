from rcmt import Context, Task, register_task


class TaskOne(Task):
    name = "task-one"

    def filter(self, ctx: Context) -> bool:
        return False

    def apply(self, ctx: Context) -> None:
        return None


register_task(TaskOne())

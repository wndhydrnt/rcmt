from rcmt import Context, Task, register_task


class TaskTwo(Task):
    # Invalid: Has the same name as the Task in task_one.py
    name = "task-one"

    def filter(self, ctx: Context) -> bool:
        return False

    def apply(self, ctx: Context) -> None:
        return None


register_task(TaskTwo())

from rcmt import Task
from rcmt.action import Own

with Task("unit-test") as task:
    task.add_action(Own(content=task.load_file("test.txt"), target="test.txt"))

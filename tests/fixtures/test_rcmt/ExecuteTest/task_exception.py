from rcmt import Task
from rcmt.action import Own

d = {}

with Task("unit-test-exception") as task:
    task.add_action(Own(content=d["unknown"], target="test.txt"))

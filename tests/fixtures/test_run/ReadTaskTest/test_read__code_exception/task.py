from rcmt import Task
from rcmt.action import Own

d = {}
v = d["key"]

with Task("unit-test") as task:
    task.add_action(Own(content="unittest", target="test.txt"))

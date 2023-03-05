from rcmt import Task
from rcmt.action import Own

with Task("unit-test", enabled=False) as task:
    task.add_action(Own(content="This is a unit test", target="test.txt"))

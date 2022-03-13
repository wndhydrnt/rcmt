from rcmt import Run
from rcmt.package.action import Own

with Run("unit-test") as run:
    run.add_action(Own(content=run.load_file("test.txt"), target="test.txt"))

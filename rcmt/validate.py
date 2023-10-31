# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from rcmt import task


def validate(task_file_paths: tuple[str, ...]) -> bool:
    result: bool = True
    for task_file_path in task_file_paths:
        try:
            task.read(task_file_path)
        except Exception as e:
            print(f"❌ Task in file {task_file_path} is invalid: {str(e)}")
            result = False

    for t in task.registry.tasks:
        print(f"✅ Task '{t.name}' is valid")

    return result

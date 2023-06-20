from rcmt import task


def validate(task_file_paths: tuple[str]) -> bool:
    result: bool = False
    for task_file_path in task_file_paths:
        try:
            t = task.read(task_file_path)
            print(f"✅ Task {t.name} in file {task_file_path} is valid")
        except Exception as e:
            print(f"❌ Task in file {task_file_path} is invalid: {str(e)}")
            result = False

    return result

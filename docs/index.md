# rcmt

rcmt automates refactorings across many repositories.

Write Python code to define how the content of files should look like. Then let rcmt
apply the changes and create merge requests.

## Features

- **Mass Refactoring** - create, update or delete files across many repositories.
- **Automation** - automatic creation of merge requests in repositories; optionally
  merge them automatically if approved and all checks have passed.
- **Flexibility** - call third-party APIs or integrate libraries.

## Quick Start

### Prerequisites

- Python 3.9 or higher (verify with `python --version`).
- A repository on GitHub or GitLab to modify.
- A [GitHub Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token)
  or a [GitLab Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token).

### Installation

```shell
pip install rcmt
rcmt version
```

Output

```
0.23.1
```

### Write the Task file

Create the file `task.py` and add the following content:

```python title="task.py"
from rcmt import Task
from rcmt.action import Own
from rcmt.matcher import RepoName

with Task(
    name="rcmt-example",
    auto_merge=False,
    pr_title="rcmt Example",
    pr_body="""This pull request has been created as part of the how-to guide:

https://rcmt.readthedocs.io/get-started/create-a-task/
"""
) as task: # (1)!
    task.add_action(Own(content="rcmt works!", target="rcmt.txt")) # (2)!
    task.add_matcher(RepoName("^github.com/wndhydrnt/rcmt-example$")) # (3)!
```

1.  A Task bundles Actions and Matchers and allows to set extra configuration.
2.  This adds an Action. Actions modify files in a repository. In this case, the `Own`
    Action creates the file `rcmt.txt` with the content `rcmt works!`.
3.  This adds a Matcher. Matchers allow filtering the repositories to which a Task
    applies. This can be the name of a repository, like in this example. Other Matchers
    are available that check for the existence of a file in a repository or the content
    of a file.

### Run rcmt

=== "GitHub"

    ```shell
    RCMT_GITHUB_ACCESS_TOKEN=xxxxx rcmt run ./task.py
    ```

=== "GitLab"

    ```shell
    RCMT_GITLAB_PRIVATE_TOKEN=xxxxx rcmt run ./task.py
    ```

Output

=== "GitHub"

    ```
    2023-09-26T19:57:20.215102Z [info     ] Matched repository             repository=github.com/wndhydrnt/rcmt-example task=rcmt-example
    2023-09-26T19:57:24.866457Z [info     ] Create pull request            repo=github.com/wndhydrnt/rcmt-example
    2023-09-26T19:57:25.637469Z [info     ] Finished processing of repositories repository_count=1
    ```

=== "GitLab"

    ```
    2023-09-26T19:57:20.215102Z [info     ] Matched repository             repository=gitlab.com/wandhydrant/rcmt-example task=rcmt-example
    2023-09-26T19:57:24.866457Z [info     ] Create pull request            repo=gitlab.com/wandhydrant/rcmt-example
    2023-09-26T19:57:25.637469Z [info     ] Finished processing of repositories repository_count=1
    ```
### View and merge the pull request

rcmt has created a pull request. Check GitHub or GitLab to inspect the changes.

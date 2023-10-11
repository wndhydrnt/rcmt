# Templating

Templating allows changing the content of PR title and PR body dynamically. The
templating engine is [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/),
which supports statements and expressions and is well known in the Python space.

## Default template variables

rcmt sets these template variables automatically:

| Name         | Description                                                                                                          | Example      |
|--------------|----------------------------------------------------------------------------------------------------------------------|--------------|
| `repo_host`  | The host of the repository.                                                                                          | `github.com` |
| `repo_owner` | In GitHub, the user or organization that owns the repository. In GitLab, the user or group that owns the repository. | `wndhydrnt`  |
| `repo_name`  | The name of the repository.                                                                                          | `rcmt`       |

## Usage

### Default template variables

```python
--8<-- "docs/examples/templating/task_default.py"
```

The task above will create a pull request with the title
```text
Demonstrate templating in rcmt
```
and the body
```text
Host: github.com

Owner: wndhydrnt

Name: rcmt
```

### Custom template variables

Matchers can set custom template variables.

```python
--8<-- "docs/examples/templating/task_custom.py"
```

Creates a pull request with the following body:

```text
Custom matcher says: Hello World
```

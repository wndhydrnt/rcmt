# Events

Event handling allow the execution of custom code if an event occurs. This is useful to
inform users that a new pull request has been created or to trigger external workflows. 

Event handlers get registered with a [Task](/reference/task/). Three events exist:

- `on_pr_closed`
- `on_pr_created`
- `on_pr_merged`

## Example

```python
--8<-- "docs/examples/event_handler/task.py"
```

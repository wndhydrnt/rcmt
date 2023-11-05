# Custom Configuration

Event Handlers and Filters can perform actions that require credentials, such as reading
data from an API or sending an e-mail.

There are two was of passing credentials to Event Handlers and Filters.

## Environment Variables

Configuration can be read from environment variables:

```python
--8<-- "docs/examples/custom_configuration/env_vars.py"
```

## Configuration File

Settings can be added to the `custom` section of the configuration file. Custom Filters
or Event Handlers call `Context.custom_config()` to retrieve it.

```yaml title="config.yaml"
--8<-- "docs/examples/custom_configuration/config.yaml"
```

```python title="task.py"
--8<-- "docs/examples/custom_configuration/file.py"
```

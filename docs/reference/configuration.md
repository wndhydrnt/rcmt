# Configuration

Configuration defines global settings of rcmt.

## Full example

All values in this example are default values.

```yaml
custom:
  key: value
database:
  connection: "sqlite:///:memory:"
  migrate: true
dry_run: false
git:
  branch_prefix: rcmt/
  clone_options: 'filter: "blob:none"'
  data_dir: /tmp/rcmt/data
  user_email: ""
  user_name: ""
github:
  access_token: ""
gitlab:
  private_token: ""
  url: https://gitlab.com
log_format: ""
log_level: info
pushgateway:
  address: "localhost:9091"
  enabled: false
  job_name: "rcmt"
```

## `custom`

Custom configuration. Filters and Event Handlers can retrieve this configuration. See
[Custom Configuration](../features/custom-config.md).

## `database`

### `connection`

Connection string to a database where rcmt stores additional data. The value is an
[SQLAlchemy Database URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>).
Defaults to ``sqlite:///:memory:``.

!!! note

    rcmt does not include database drivers like `psycopg2` or `mysqlclient`. These
    packages need to be installed separately.

### `migrate`

Run migrations at the start of rcmt. Defaults to `true`.

## `dry_run`

Matches repositories, checks them out and applies actions but does not create pull
requests. Defaults to `false`.

## `git`

### `branch_prefix`

Prefix of git branches that rcmt creates. Not used if a Task defines its own
`branch_name`. Defaults to `rcmt/`.

### `clone_options`

Key/value pairs to pass as additional flags to `git clone`.

See the [official docs](https://www.git-scm.com/docs/git-clone) on `git clone` for all
available flags.

Defaults to
```
filter: "blob:none"
```

## `data_dir`

Path to a directory where rcmt stores its temporary data, like checkouts of
repositories. Defaults to `/tmp/rcmt/data`.

## `user_email`

E-mail to set when committing changes. Defaults to `""`.

## `user_name`

Name of the author to set when committing changes. Defaults to `rcmt`.

## `github`

### `access_token`

Access token to authenticate at the GitHub API.

## `gitlab`

### `private_token`

Private token to authenticate at the GitLab API.

### `url`

URL of the GitLab installation. Defaults to `https://gitlab.com`.

## `log_format`

Format of log records. If not set, rcmt will auto-detect if it is run from a terminal
and pretty-print records. Otherwise, it uses JSON.

Set to `json` to force JSON format.

Set to `console` to force pretty-printing of log records.

## `log_level`

Log level of the application. Defaults to `info`.

## `pr_title_prefix`

rcmt prefixes every Pull Request title with this string. Defaults to `rcmt:`.

## `pr_title_body`

rcmt uses this string to set the title of each Pull Request. Defaults to
`apply task {matcher_name}`.

`matcher_name` is a variable referencing the name of a [Task](./task.md). No
other variables are supported at the moment.

## `pr_title_suffix`

rcmt suffixes every Pull Request title with this string. Defaults to `""`.

## `pushgateway`

Send metrics to a [Prometheus Pushgateway](https://github.com/prometheus/pushgateway).

### `address`

The address of the Pushgateway.
Defaults to `localhost:9091`.

### `enabled`

Set to `true` to enable sending metrics to a Pushgateway.
Defaults to `false`.

### `job_label`

Configure the value of the `job` label added to each metric.
Defaults to `rcmt`.

See [About the job and instance labels](https://github.com/prometheus/pushgateway#about-the-job-and-instance-labels)
for an explanation of the label.

## Environment Variables

rcmt can read settings from environment variables. An environment variable has to start
with `RCMT_`. `_` separates subsections.

!!! note
   
    Values set in the configuration file take precedence over environment variables.

### Example

```shell
export RCMT_DRY_RUN=true
export RCMT_LOG_LEVEL=warn
export RCMT_GITHUB_ACCESS_TOKEN=xxxxx
```

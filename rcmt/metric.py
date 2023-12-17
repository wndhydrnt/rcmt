# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
rcmt can collect metrics on each of its runs and send them to a Prometheus Pushgateway.

See [pushgateway configuration](https://rcmt.readthedocs.io/en/latest/operations/metrics/)
for how to configure sending metrics.

The following metrics are recorded:

- `rcmt_run_start_timestamp` - Unix timestamp at which the latest run started.
- `rcmt_run_finish_timestamp` - Unix timestamp at which the latest run finished.
- `rcmt_run_repositories_processed` - Repositories processed by the latest run of rcmt.
- `rcmt_run_error` - Result of the latest run of rcmt.
   0 indicates success, 1 indicates an error.

On each run, a unique label `run_id` is created and attached to each of the metrics.
The label can be used to differentiate between runs when querying metrics via Prometheus.
"""

import random
import string

import structlog
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from rcmt import config

log: structlog.stdlib.BoundLogger = structlog.get_logger(package="metric")

label_run = "".join(
    random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
)
registry = CollectorRegistry()

run_start_timestamp = Gauge(
    name="rcmt_run_start_timestamp",
    documentation="Unix timestamp at which the latest run started.",
    labelnames=["run_id"],
    registry=registry,
).labels(label_run)

run_finish_timestamp = Gauge(
    name="rcmt_run_finish_timestamp",
    documentation="Unix timestamp at which the latest run finished.",
    labelnames=["run_id"],
    registry=registry,
).labels(label_run)

run_repositories_processed = Gauge(
    name="rcmt_run_repositories_processed",
    documentation="Repositories processed by the latest run of rcmt.",
    labelnames=["run_id"],
    registry=registry,
).labels(label_run)

run_error = Gauge(
    name="rcmt_run_error",
    documentation="Result of the latest run of rcmt. 0 indicates success, 1 indicates an error.",
    labelnames=["run_id"],
    registry=registry,
).labels(label_run)


def push(cfg: config.Pushgateway) -> None:
    if cfg.enabled is False:
        return None

    log.debug("Sending metrics to pushgateway")
    push_to_gateway(
        gateway=cfg.address,
        job=cfg.job_label,
        registry=registry,
    )

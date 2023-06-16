import logging
import sys
from typing import Any, Mapping, MutableMapping

import structlog


class SecretMasker:
    def __init__(self):
        self.secrets: list[str] = []

    def add_secret(self, s: str) -> None:
        self.secrets.append(s)

    def process_event(
        self, _, __, event_dict: MutableMapping[str, Any]
    ) -> Mapping[str, Any]:
        for k, v in event_dict.items():
            if not isinstance(v, str):
                continue

            for secret in self.secrets:
                if secret in v:
                    event_dict[k] = v.replace(secret, "****")

        return event_dict


SECRET_MASKER = SecretMasker()


def configure(log_level: str):
    processors = [
        # If log level is too low, abort pipeline and throw away log entry.
        structlog.stdlib.filter_by_level,
        # Add the name of the logger to event dict.
        structlog.stdlib.add_logger_name,
        # Add log level to event dict.
        structlog.stdlib.add_log_level,
        # Perform %-style formatting.
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Add a timestamp in ISO 8601 format.
        structlog.processors.TimeStamper(fmt="iso"),
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        structlog.processors.StackInfoRenderer(),
        # If the "exc_info" key in the event dict is either true or a
        # sys.exc_info() tuple, remove "exc_info" and render the exception
        # with traceback into the "exception" key.
        structlog.processors.format_exc_info,
        # If some value is in bytes, decode it to a unicode str.
        structlog.processors.UnicodeDecoder(),
        # Add callsite parameters.
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.processors.EventRenamer("message"),
    ]

    processors.append(structlog.processors.JSONRenderer())
    # if sys.stderr.isatty():
    #     processors.append(structlog.dev.ConsoleRenderer())
    # else:
    #     processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        # `wrapper_class` is the bound logger that you get back from
        # get_logger(). This one imitates the API of `logging.Logger`.
        wrapper_class=structlog.stdlib.BoundLogger,
        # `logger_factory` is used to create wrapped loggers that are used for
        # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
        # string) from the final processor (`JSONRenderer`) will be passed to
        # the method of the same name as that you've called on the bound logger.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Effectively freeze configuration after creating the first bound
        # logger.
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=log_level.upper(),
    )

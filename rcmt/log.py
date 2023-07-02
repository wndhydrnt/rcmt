import logging
import sys
from typing import Any, Mapping, MutableMapping, Optional

import structlog


class SecretMasker:
    def __init__(self) -> None:
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


def configure(format: Optional[str], level: str) -> None:
    processors = [
        SECRET_MASKER.process_event,
        structlog.processors.add_log_level,
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
    ]

    use_json = False
    if format is None:
        if sys.stderr.isatty() is False:
            use_json = True
    else:
        if format.lower() == "json":
            use_json = True

    if use_json is True:
        processors.append(structlog.processors.EventRenamer("message"))
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=sys.stderr is not None and sys.stderr.isatty()
            )
        )

    log_level = logging.getLevelName(level.upper())
    structlog.configure(
        processors=processors,  # type: ignore
        # `wrapper_class` is the bound logger that you get back from
        # get_logger(). This one imitates the API of `logging.Logger`.
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        # `logger_factory` is used to create wrapped loggers that are used for
        # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
        # string) from the final processor (`JSONRenderer`) will be passed to
        # the method of the same name as that you've called on the bound logger.
        logger_factory=structlog.PrintLoggerFactory(sys.stderr),
        # Effectively freeze configuration after creating the first bound
        # logger.
        cache_logger_on_first_use=True,
    )

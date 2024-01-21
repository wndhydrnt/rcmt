# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import logging.config
import sys
from typing import Any, MutableMapping, Optional

_CONTEXT_VARS: dict[str, Any] = {}


logging_config: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s%(reset)s %(bold_white)s%(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(levelname)s %(name)s %(message)s",
            "rename_fields": {"levelname": "level", "name": "logger"},
        },
        "standard": {"format": "%(levelname)-8s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "WARNING", "propagate": True},
        "rcmt": {
            "handlers": ["default"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


def configure(log_format: Optional[str], level: str) -> None:
    handlers: dict = logging_config.get("handlers", {})
    handler_default = handlers.get("default", {})
    handler_default["formatter"] = detect_formatter(log_format)

    loggers: dict = logging_config.get("loggers", {})
    logger_rcmt = loggers.get("rcmt", {})
    logger_rcmt["level"] = level.upper()
    logging.config.dictConfig(logging_config)


def detect_formatter(log_format: Optional[str]) -> str:
    is_tty = sys.stderr.isatty()
    if log_format is None:
        if is_tty is True:
            return "colored"
        else:
            return "json"

    if log_format.lower() == "json":
        return "json"

    if log_format.lower() == "console" and is_tty is True:
        return "colored"

    return "standard"


class ContextAwareAdapter(logging.LoggerAdapter):
    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        try:
            extra: dict = kwargs["extra"]
            for k, v in extra.items():
                msg = f"{msg} {k}={v}"
        except KeyError:
            pass

        for k, v in _CONTEXT_VARS.items():
            msg = f"{msg} {k}={v}"

        return msg, kwargs


def bind_contextvars(**kwargs) -> None:
    for k, v in kwargs.items():
        _CONTEXT_VARS[k] = v


def clear_contextvars() -> None:
    global _CONTEXT_VARS
    _CONTEXT_VARS.clear()


def get_logger(name: str) -> ContextAwareAdapter:
    # Python 3.9 requires `extra` to be a `dict`. Could be `None` in 3.10 and higher.
    return ContextAwareAdapter(logger=logging.getLogger(name), extra={})

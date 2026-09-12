"""Non-secret application configuration."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class ConfigurationError(ValueError):
    """Raised when a non-secret application setting is invalid."""


class Environment(StrEnum):
    """Supported deployment contexts."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


_LOG_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"})


@dataclass(frozen=True)
class ApplicationConfig:
    """Validated settings that are safe to obtain from environment variables."""

    environment: Environment
    log_level: str
    event_schema_version: int

    @classmethod
    def from_environment(cls, environ: Mapping[str, str] | None = None) -> ApplicationConfig:
        """Build configuration from non-secret environment variables."""
        values = os.environ if environ is None else environ
        environment = _parse_environment(values.get("CLOUDSCALE_ENVIRONMENT", Environment.LOCAL))
        log_level = _parse_log_level(values.get("CLOUDSCALE_LOG_LEVEL", "INFO"))
        schema_version = _parse_schema_version(values.get("CLOUDSCALE_EVENT_SCHEMA_VERSION", "1"))
        return cls(
            environment=environment,
            log_level=log_level,
            event_schema_version=schema_version,
        )


def _parse_environment(value: str | Environment) -> Environment:
    try:
        return Environment(value.lower())
    except ValueError as error:
        valid_environments = ", ".join(environment.value for environment in Environment)
        message = f"CLOUDSCALE_ENVIRONMENT must be one of: {valid_environments}."
        raise ConfigurationError(message) from error


def _parse_log_level(value: str) -> str:
    log_level = value.upper()
    if log_level not in _LOG_LEVELS:
        valid_levels = ", ".join(sorted(_LOG_LEVELS))
        message = f"CLOUDSCALE_LOG_LEVEL must be one of: {valid_levels}."
        raise ConfigurationError(message)
    return log_level


def _parse_schema_version(value: str) -> int:
    try:
        schema_version = int(value)
    except ValueError as error:
        message = "CLOUDSCALE_EVENT_SCHEMA_VERSION must be a positive integer."
        raise ConfigurationError(message) from error

    if schema_version < 1:
        message = "CLOUDSCALE_EVENT_SCHEMA_VERSION must be a positive integer."
        raise ConfigurationError(message)
    return schema_version

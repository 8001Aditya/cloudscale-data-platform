import pytest

from cloudscale_data_platform.config import ApplicationConfig, ConfigurationError, Environment


def test_from_environment_uses_safe_local_defaults() -> None:
    config = ApplicationConfig.from_environment({})

    assert config.environment is Environment.LOCAL
    assert config.log_level == "INFO"
    assert config.event_schema_version == 1


def test_from_environment_normalizes_valid_values() -> None:
    config = ApplicationConfig.from_environment(
        {
            "CLOUDSCALE_ENVIRONMENT": "development",
            "CLOUDSCALE_LOG_LEVEL": "debug",
            "CLOUDSCALE_EVENT_SCHEMA_VERSION": "2",
        }
    )

    assert config.environment is Environment.DEVELOPMENT
    assert config.log_level == "DEBUG"
    assert config.event_schema_version == 2


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("CLOUDSCALE_ENVIRONMENT", "staging"),
        ("CLOUDSCALE_LOG_LEVEL", "verbose"),
        ("CLOUDSCALE_EVENT_SCHEMA_VERSION", "0"),
        ("CLOUDSCALE_EVENT_SCHEMA_VERSION", "one"),
    ],
)
def test_from_environment_rejects_invalid_values(name: str, value: str) -> None:
    with pytest.raises(ConfigurationError):
        ApplicationConfig.from_environment({name: value})

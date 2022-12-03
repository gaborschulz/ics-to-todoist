# pylint: disable-all
import re
import tomllib
from zoneinfo import ZoneInfo

import pytest

from ics_to_todoist.models import Configuration


@pytest.fixture
def configuration(monkeypatch):
    monkeypatch.setenv("TODOIST_API_KEY", "TEST_KEY")

    with open('data/test_config.toml', 'rb') as conf:
        config_json = tomllib.load(conf)
    config = Configuration(**config_json, )
    return config


@pytest.fixture
def configuration_no_timezone(monkeypatch):
    monkeypatch.setenv("TODOIST_API_KEY", "TEST_KEY")

    with open('data/test_config.toml', 'rb') as conf:
        config_json = tomllib.load(conf)
    config_json.pop('timezone')
    config = Configuration(**config_json, )
    return config


def test_configuration_timezone(configuration):
    assert configuration.zoneinfo == ZoneInfo(configuration.timezone)


def test_relevant_names_regex(configuration):
    assert configuration.relevant_names_regex == re.compile(configuration.relevant_names)


def test_todoist_api_key_env_var_usage(configuration):
    assert configuration.todoist_api_key == 'TEST_KEY'


def test_default_timezone(configuration_no_timezone):
    assert configuration_no_timezone.timezone == 'UTC'


def test_missing_todoist_api_key_raises_validation_error():
    with open('data/test_config.toml', 'rb') as conf:
        config_json = tomllib.load(conf)

        if 'todoist_api_key' in config_json:
            config_json.pop('todoist_api_key')
        with pytest.raises(Exception):
            config = Configuration(**config_json, )

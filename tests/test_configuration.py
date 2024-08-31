# pylint: disable-all
import os
import re
from zoneinfo import ZoneInfo

import pytest

from ics_to_todoist.models import Configuration


@pytest.fixture
def configuration_no_timezone(monkeypatch, config_json):
    monkeypatch.setenv("TODOIST_API_KEY", "TEST_KEY")

    config_json.pop('timezone')
    config = Configuration(**config_json)
    return config


def test_configuration_timezone(config):
    assert config.zoneinfo == ZoneInfo(config.timezone)


def test_relevant_names_regex(config):
    assert config.relevant_names_regex == re.compile(config.relevant_names)


def test_todoist_api_key_env_var_usage(config):
    assert config.todoist_api_key == 'TEST_KEY'


def test_default_timezone(configuration_no_timezone):
    assert configuration_no_timezone.timezone == 'UTC'


def test_missing_todoist_api_key_raises_validation_error(monkeypatch, config_json):
    if 'todoist_api_key' in config_json:
        config_json.pop('todoist_api_key')
    if os.getenv('TODOIST_API_KEY', ''):
        monkeypatch.delenv('TODOIST_API_KEY')
    with pytest.raises(Exception):
        _ = Configuration(**config_json, )

# pylint: disable-all
import tomllib
from typing import Any, Tuple

import pytest

from ics_to_todoist.__main__ import load_config
from ics_to_todoist.models import Configuration


@pytest.fixture
def configuration(monkeypatch) -> Tuple[dict[str, Any], Configuration]:
    monkeypatch.setenv("TODOIST_API_KEY", "TEST_KEY")
    config_file = 'data/test_config.toml'
    with open(config_file, 'rb') as conf:
        config_json = tomllib.load(conf)

    config = load_config(config_file=config_file)

    return config_json, config


def test_load_config(configuration):
    config_json, config = configuration
    assert config.relevant_names == config_json['relevant_names']
    assert config.target_project == config_json['target_project']
    assert config.default_reminder == config_json['default_reminder']
    assert config.timezone == config_json['timezone']
    assert config.only_future_events == config_json['only_future_events']

# Test what happens when todoist project is not found
# Test if ics does not return any relevant values
# Test what happens if there is not time provided for an event and default_reminder is set to true

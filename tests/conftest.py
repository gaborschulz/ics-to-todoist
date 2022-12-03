# pylint: disable-all
import tomllib
from typing import Any

import pytest

from ics_to_todoist.models import Configuration


@pytest.fixture
def config_json() -> dict[str, Any]:
    config_file = 'data/test_config.toml'
    with open(config_file, 'rb') as conf:
        config_json = tomllib.load(conf)

    return config_json


@pytest.fixture
def config(monkeypatch, config_json) -> Configuration:
    monkeypatch.setenv("TODOIST_API_KEY", "TEST_KEY")
    configuration = Configuration(**config_json)

    return configuration

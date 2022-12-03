# pylint: disable-all
import tomllib
from datetime import datetime
from typing import Any, Tuple
from zoneinfo import ZoneInfo

import pytest

from ics_to_todoist.__main__ import load_config, load_ics_data
from ics_to_todoist.models import Configuration, Event


@pytest.fixture
def configuration(monkeypatch) -> Tuple[dict[str, Any], Configuration]:
    monkeypatch.setenv("TODOIST_API_KEY", "TEST_KEY")
    config_file = 'data/test_config.toml'
    with open(config_file, 'rb') as conf:
        config_json = tomllib.load(conf)

    config = load_config(config_file=config_file)

    return config_json, config


@pytest.fixture
def full_ics_dataset(configuration) -> list[Event]:
    _, config = configuration
    ics_file = 'data/test.ics'
    events = load_ics_data(ics_file=ics_file, config=config)
    return events


def test_load_config(configuration):
    config_json, config = configuration
    assert config.relevant_names == config_json['relevant_names']
    assert config.target_project == config_json['target_project']
    assert config.default_reminder == config_json['default_reminder']
    assert config.timezone == config_json['timezone']
    assert config.only_future_events == config_json['only_future_events']


def test_all_events_loaded(full_ics_dataset):
    assert len(full_ics_dataset) == 3


def test_all_events_names_match(full_ics_dataset):
    event_names = [x.name for x in full_ics_dataset]
    assert 'Relevant future event' in event_names
    assert 'Irrelevant event' in event_names
    assert 'Past event' in event_names


def test_event_begin_dates_past(full_ics_dataset):
    events = [x for x in full_ics_dataset if x.begin <= datetime(2022, 12, 31, tzinfo=ZoneInfo('Europe/Berlin'))]
    assert len(events) == 1


def test_event_begin_dates_future(full_ics_dataset):
    events = [x for x in full_ics_dataset if x.begin > datetime(2022, 12, 31, tzinfo=ZoneInfo('Europe/Berlin'))]
    assert len(events) == 2


def test_event_begin_dates_zoneinfo(full_ics_dataset, configuration):
    _, config = configuration
    assert full_ics_dataset.pop().begin.tzinfo == ZoneInfo(config.timezone)

# Test what happens when todoist project is not found
# Test if ics does not return any relevant values
# Test what happens if there is not time provided for an event and default_reminder is set to true

# pylint: disable-all
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from ics_to_todoist.__main__ import load_ics_data, filter_events, load_config
from ics_to_todoist.models import Event


@pytest.fixture
def full_ics_dataset(config) -> list[Event]:
    ics_file = 'data/test.ics'
    events = load_ics_data(ics_file=ics_file, config=config)
    return events


def test_load_config(config_json):
    config = load_config(config_file='data/test_config.toml')
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


def test_event_begin_dates_zoneinfo(full_ics_dataset, config):
    assert full_ics_dataset.pop().begin.tzinfo == ZoneInfo(config.timezone)


def test_filter_events_count(full_ics_dataset, config):
    events = filter_events(events=full_ics_dataset, config=config)
    assert len(events) == 1


def test_filter_events_only_future(full_ics_dataset, config):
    events = [x.begin >= datetime(2022, 12, 31, tzinfo=ZoneInfo('Europe/Berlin')) for x in filter_events(events=full_ics_dataset, config=config)]
    assert all(events)


def test_filter_events_correct_names(full_ics_dataset, config):
    events = [x.name for x in filter_events(events=full_ics_dataset, config=config)]
    assert events[0] == 'Relevant future event'

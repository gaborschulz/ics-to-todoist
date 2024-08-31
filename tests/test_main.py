# pylint: disable-all
import tomllib
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from ics import Calendar
from typer.testing import CliRunner

import ics_to_todoist
from ics_to_todoist import __main__
from ics_to_todoist.__main__ import app
from ics_to_todoist.models import Configuration, Event

load_dotenv('.env.test')


def test_main_function_no_params():
    runner = CliRunner()
    result = runner.invoke(app)
    assert result.exit_code != 0


def test_main_function_version():
    runner = CliRunner()
    result = runner.invoke(app, ['--version'])
    assert __main__.__version__ in result.stdout
    assert result.exit_code == 0


def test_main_function_missing_config():
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics'])
    assert result.exit_code != 0


def test_main_function_all_arguments_provided():
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert result.exit_code == 0


def test_main_function_load_config(monkeypatch):
    load_config_invoked = False

    def fake_load_config(config_file: str) -> Configuration:
        with open(config_file, 'rb') as conf:
            config_json = tomllib.load(conf)
        config = Configuration(**config_json, )

        nonlocal load_config_invoked
        load_config_invoked = True

        return config

    monkeypatch.setattr(ics_to_todoist.__main__, 'load_config', fake_load_config)
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert result.exit_code == 0
    assert 'Loaded configuration from file' in result.stdout
    assert load_config_invoked


def test_main_function_load_config_validationerror(monkeypatch):
    monkeypatch.delenv('TODOIST_API_KEY')

    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert result.exit_code != 0
    assert 'TODOIST_API_KEY environment variable has to be set or the todoist_api_key field has to be provided' in result.stdout


def test_main_function_load_ics_data(monkeypatch):
    load_ics_data_invoked = False

    def fake_load_ics_data(ics_file: str, config: Configuration) -> list[Event]:
        with Path(ics_file).open('r', encoding='utf-8') as fp:  # pylint: disable=invalid-name
            file_content = fp.read()

        events: list[Event] = []
        calendar = Calendar(file_content)

        for cal_event in calendar.events:
            event = Event(uid=cal_event.uid, name=cal_event.name, description=cal_event.description,
                          begin=cal_event.begin.datetime.astimezone(config.zoneinfo), end=cal_event.end.datetime.astimezone(config.zoneinfo),
                          location=cal_event.location, precision=cal_event._begin_precision)  # pylint: disable=protected-access
            events.append(event)

        nonlocal load_ics_data_invoked
        load_ics_data_invoked = True

        return events

    monkeypatch.setattr(ics_to_todoist.__main__, 'load_ics_data', fake_load_ics_data)
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert result.exit_code == 0
    assert 'Loaded .ics file data/test.ics. Found 3 events' in result.stdout
    assert load_ics_data_invoked


def test_main_function_filter_events_nonzero(monkeypatch):
    filter_events_invoked = False

    def fake_filter_events(events: list[Event], config: Configuration) -> list[Event]:
        filtered_events = events
        if config.only_future_events:
            filtered_events = [event for event in filtered_events if event.begin >= datetime.now(tz=config.zoneinfo)]
        if config.relevant_names:
            filtered_events = [event for event in filtered_events if config.relevant_names_regex.findall(event.name)]

        nonlocal filter_events_invoked
        filter_events_invoked = True
        return filtered_events

    monkeypatch.setattr(ics_to_todoist.__main__, 'filter_events', fake_filter_events)
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert result.exit_code == 0
    assert 'Filtered events. 1 event(s) remaining' in result.stdout
    assert filter_events_invoked


def test_main_function_filter_events_zero(monkeypatch):
    def fake_filter_events(events: list[Event], config: Configuration) -> list[Event]:
        return []

    monkeypatch.setattr(ics_to_todoist.__main__, 'filter_events', fake_filter_events)
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert result.exit_code == 0
    assert 'Filtered events. 0 event(s) remaining' in result.stdout
    assert 'Found target project' not in result.stdout


def test_main_function_todoist_api(config_json):
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert 'DRY RUN: no actual upload performed' in result.stdout
    assert result.exit_code == 0


def test_main_function_invalid_project_name(monkeypatch):
    def fake_load_config(config_file: str) -> Configuration:
        with open(config_file, 'rb') as conf:
            config_json = tomllib.load(conf)
        config = Configuration(**config_json, )

        config.target_project = 'INVALID_PROJECT_NAME'
        return config

    monkeypatch.setattr(ics_to_todoist.__main__, 'load_config', fake_load_config)
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml', '--dry-run'])
    assert result.exit_code == 1
    assert 'ERROR: list index out of range' in result.stdout


def test_main_function_todoist_api_non_dryrun(config_json):
    runner = CliRunner()
    result = runner.invoke(app, ['data/test.ics', '--config-file', 'data/test_config.toml'])
    assert f'Found target project {config_json["target_project"]}:' in result.stdout
    assert result.exit_code == 0

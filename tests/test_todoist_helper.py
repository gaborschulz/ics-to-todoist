# pylint: disable-all
import os
from typing import Any

import pytest
from dotenv import load_dotenv
from rich.progress import Progress
from todoist import TodoistAPI

import ics_to_todoist.todoist_helper
from ics_to_todoist.__main__ import load_ics_data, filter_events
from ics_to_todoist.models import Event
from ics_to_todoist.todoist_helper import get_project_by_name, upload_events

patched_projects: dict[str, Any] = {}


@pytest.fixture
def todoist_api(monkeypatch) -> TodoistAPI:
    load_dotenv()
    monkeypatch.setattr(ics_to_todoist.todoist_helper, 'projects', patched_projects)
    api = TodoistAPI(os.getenv('TODOIST_API_KEY'))
    monkeypatch.setattr(api, 'commit', lambda: None)
    return api


@pytest.fixture
def full_ics_dataset(config) -> list[Event]:
    ics_file = 'data/test.ics'
    events = load_ics_data(ics_file=ics_file, config=config)
    return events


@pytest.fixture
def filtered_events(full_ics_dataset, config) -> list[Event]:
    return filter_events(full_ics_dataset, config)


def test_get_project_by_name_success(todoist_api):
    project = get_project_by_name(todoist_api, 'Inbox')
    assert project


def test_get_project_by_name_raises_exception(todoist_api):
    with pytest.raises(ValueError):
        project = get_project_by_name(todoist_api, 'INVALID_PROJECT_NAME')


def test_upload_events_no_default_reminder(todoist_api, filtered_events, config):
    project = get_project_by_name(todoist_api, 'Inbox')
    result = upload_events(todoist_api, project, filtered_events, config, Progress())
    reminder_queue = [x['args']['due_date_utc'] for x in todoist_api.queue if x['type'] == 'reminder_add']
    auto_reminder = [x['args']['auto_reminder'] for x in todoist_api.queue if x['type'] == 'item_add']
    assert not any(auto_reminder)
    assert len(reminder_queue) == len(config.reminder_times)
    assert result == 1


def test_upload_events_default_reminder(todoist_api, filtered_events, config):
    project = get_project_by_name(todoist_api, 'Inbox')
    config.default_reminder = True
    result = upload_events(todoist_api, project, filtered_events, config, Progress())
    auto_reminder = [x['args']['auto_reminder'] for x in todoist_api.queue if x['type'] == 'item_add']
    assert all(auto_reminder)
    assert result == 1

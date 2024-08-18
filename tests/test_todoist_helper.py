# pylint: disable-all
import os

import pytest
from dotenv import load_dotenv
from rich.progress import Progress
from todoist_api_python.api import TodoistAPI

from ics_to_todoist.__main__ import load_ics_data, filter_events
from ics_to_todoist.models import Event
from ics_to_todoist.todoist_helper import upload_events


@pytest.fixture
def todoist_api(monkeypatch) -> TodoistAPI:
    load_dotenv('.env.test')
    api = TodoistAPI(token=os.getenv('TODOIST_API_KEY'))  # type: ignore
    return api


@pytest.fixture
def full_ics_dataset(config) -> list[Event]:
    ics_file = 'data/test.ics'
    events = load_ics_data(ics_file=ics_file, config=config)
    return events


@pytest.fixture
def filtered_events(full_ics_dataset, config) -> list[Event]:
    return filter_events(full_ics_dataset, config)


def test_upload_events_no_default_reminder(todoist_api, filtered_events, config):
    project = [x for x in todoist_api.get_projects() if x.name == 'Inbox'][0]
    result = upload_events(todoist_api, project, filtered_events, config, Progress())
    # reminder_queue = [x['args']['due_date_utc'] for x in todoist_api.queue if x['type'] == 'reminder_add']
    # auto_reminder = [x['args']['auto_reminder'] for x in todoist_api.queue if x['type'] == 'item_add']
    # assert not any(auto_reminder)
    # assert len(reminder_queue) == len(config.reminder_times)
    assert result == 1

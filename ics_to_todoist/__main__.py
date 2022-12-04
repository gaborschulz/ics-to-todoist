# pylint: disable=wrong-import-order
import sys
import tomllib
from datetime import datetime
from pathlib import Path

import typer
from ics import Calendar
from pydantic import ValidationError
from rich.console import Console
from rich.progress import Progress
from todoist import TodoistAPI

from ics_to_todoist.models import Event, Configuration
from ics_to_todoist.todoist_helper import get_project_by_name, upload_events

app = typer.Typer()


def load_ics_data(ics_file: str, config: Configuration) -> list[Event]:
    """ Load ics file into a list of events"""
    with Path(ics_file).open('r', encoding='utf-8') as fp:  # pylint: disable=invalid-name
        file_content = fp.read()

    events: list[Event] = []
    calendar = Calendar(file_content)

    for cal_event in calendar.events:
        event = Event(uid=cal_event.uid, name=cal_event.name, description=cal_event.description,
                      begin=cal_event.begin.datetime.astimezone(config.zoneinfo), end=cal_event.end.datetime.astimezone(config.zoneinfo),
                      location=cal_event.location, precision=cal_event._begin_precision)  # pylint: disable=protected-access
        events.append(event)

    return events


def load_config(config_file: str) -> Configuration:
    """ Load configuration from toml file """
    with open(config_file, 'rb') as conf:
        config_json = tomllib.load(conf)
    config = Configuration(**config_json, )
    return config


def filter_events(events: list[Event], config: Configuration) -> list[Event]:
    """ Filter events based on the configuration """
    filtered_events = events
    if config.only_future_events:
        filtered_events = [event for event in filtered_events if event.begin >= datetime.now(tz=config.zoneinfo)]
    if config.relevant_names:
        filtered_events = [event for event in filtered_events if config.relevant_names_regex.findall(event.name)]

    return filtered_events


@app.command()
def main(ics_file: str, config_file: str = typer.Option(..., help="Path of the config file (TOML)"), dryrun: bool = typer.Option(False, "--dry-run")):
    """ Main function """
    console = Console()
    with console.status(f'Reading configuration from file [bold yellow]{config_file}[/bold yellow]...'):
        try:
            config = load_config(config_file=config_file)
        except ValidationError as ex:
            print(ex)
            sys.exit(1)
        console.print(f'Loaded configuration from file [bold yellow]{config_file}[/bold yellow]')
    with console.status(f'Reading .ics file [bold yellow]{ics_file}[/bold yellow]...'):
        events = load_ics_data(ics_file=ics_file, config=config)
        console.print(f'Loaded .ics file [bold yellow]{ics_file}[/bold yellow]. Found {len(events)} events')
    with console.status('Filtering events...'):
        events = filter_events(events=events, config=config)
        console.print(f'Filtered events. {len(events)} event(s) remaining')
        if len(events) == 0:
            sys.exit(0)
    with console.status('Syncing with Todoist...'):
        api = TodoistAPI(config.todoist_api_key)  # types: ignore
        api.sync()
        try:
            project = get_project_by_name(api, config.target_project)
            console.print(f'Found target project [bold yellow]{config.target_project}[/bold yellow]: {project.name}')
        except ValueError as ex:
            print(ex)
            sys.exit(1)
    with Progress() as progress:
        if not dryrun:
            upload_events(api, project, events, config, progress)
        else:
            console.print('DRY RUN: no actual upload performed')

    console.print('Done')


if __name__ == "__main__":  # pragma: no cover
    app()

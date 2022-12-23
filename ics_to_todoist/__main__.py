# pylint: disable=wrong-import-order
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Optional

import pkg_resources
import typer
from ics import Calendar
from pydantic import ValidationError
from rich.console import Console
from rich.progress import Progress
from synctodoist import TodoistAPI
from synctodoist.exceptions import TodoistError

from ics_to_todoist.models import Event, Configuration
from ics_to_todoist.todoist_helper import upload_events

app = typer.Typer()

__version__ = pkg_resources.get_distribution("ics-to-todoist").version


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


def version_callback(value: bool):
    """Callback to show the tool's version"""
    if value:
        print(f'ics-to-todoist version: {__version__}')
        raise typer.Exit()


@app.command()
def main(ics_file: str,
         config_file: str = typer.Option(..., help='Path of the config file (TOML)'),
         dryrun: bool = typer.Option(False, '--dry-run', help='Execute all actions, except uploading to Todoist'),
         version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True,  # pylint: disable=unused-argument
                                                help='Show the tool\'s version')):
    """ Main function """
    console = Console()
    with console.status(f'Reading configuration from file [bold yellow]{config_file}[/bold yellow]...'):
        try:
            config = load_config(config_file=config_file)
        except ValidationError as ex:
            print(ex)
            raise typer.Exit(1)
        console.print(f'Loaded configuration from file [bold yellow]{config_file}[/bold yellow]')
    with console.status(f'Reading .ics file [bold yellow]{ics_file}[/bold yellow]...'):
        events = load_ics_data(ics_file=ics_file, config=config)
        console.print(f'Loaded .ics file [bold yellow]{ics_file}[/bold yellow]. Found {len(events)} events')
    with console.status('Filtering events...'):
        events = filter_events(events=events, config=config)
        console.print(f'Filtered events. {len(events)} event(s) remaining')
        if len(events) == 0:
            raise typer.Exit(0)
    with console.status('Syncing with Todoist...'):
        api = TodoistAPI(api_key=config.todoist_api_key)  # types: ignore
        api.sync()
        try:
            project = api.projects.find(pattern=config.target_project)
            console.print(f'Found target project [bold yellow]{config.target_project}[/bold yellow]: {project.name}')
        except TodoistError:
            console.print(f'[bold red]ERROR[/bold red]: Project {config.target_project} was not found')
            raise typer.Exit(1)  # pylint: disable=raise-missing-from
        except Exception as ex:
            console.print(f'ERROR: {ex}')
            raise typer.Exit(1)
    with Progress() as progress:
        if not dryrun:
            try:
                upload_events(api, project, events, config, progress)
            except Exception as ex:
                print(f'[bold red]ERROR[/bold red]: {ex}')
                raise typer.Exit(1)
        else:
            console.print('DRY RUN: no actual upload performed')

    console.print('Done')


if __name__ == "__main__":  # pragma: no cover
    app()

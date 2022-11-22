import re

from todoist import TodoistAPI

from ics_to_todoist.models import Event, Configuration, Project

projects: dict[str, Project] = {}


def get_project_by_name(api: TodoistAPI, project_name: str):
    """ Get project by name """
    if project_name in projects:
        return projects[project_name]

    for project in api.state["projects"]:
        if re.match(project_name, project["name"][0:len(project_name)], flags=re.IGNORECASE):
            projects[project_name] = Project(**project.data)
            return projects[project_name]

    return None


def upload_events(api: TodoistAPI, project: Project, events: list[Event], config: Configuration):
    """ Upload events to Todoist"""
    pass

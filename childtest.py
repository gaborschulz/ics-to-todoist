from dotenv import load_dotenv
import os
import re
from todoist.api import TodoistAPI


def get_project_by_name(api: TodoistAPI, target_project: str):
    for project in api.projects.state["projects"]:
        if re.fullmatch(target_project, project["name"], flags=re.IGNORECASE):
            return project["id"]

    return None


def main():
    load_dotenv()

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(api, 'Work 🔋')
    item_p = api.items.add('Task1', project_id)

    item_c = api.items.add('Task2', project_id, indent=2, parent=item_p)
    api.commit()


if __name__ == '__main__':
    main()

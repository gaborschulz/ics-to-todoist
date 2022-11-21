import os

from dotenv import load_dotenv
from todoist.api import TodoistAPI

from .shared import get_project_by_name


def main():
    """ Main function """
    load_dotenv()

    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_id = get_project_by_name(api, 'Work 🔋')
    item_p = api.items.add('Task1', project_id)  # pylint: disable=too-many-function-args

    api.items.add('Task2', project_id, indent=2, parent=item_p)  # pylint: disable=too-many-function-args
    api.commit()


if __name__ == '__main__':
    main()

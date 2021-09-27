from dotenv import load_dotenv
import os
from todoist.api import TodoistAPI
from collections import namedtuple
from datetime import date
import shared

Goal = namedtuple('Goal', ['pk', 'name', 'rationale', 'category_id', 'target_date', 'priority', 'task_id'])

goals = [
    Goal(
        pk=1, 
        name='Test Goal', 
        rationale='Test rationale',
        category_id='Development', 
        target_date=date(2023, 12, 31), 
        priority='tertiary', 
        task_id=5190001137
    )
]

def main():
    load_dotenv()
    todoist_apikey = os.getenv("TODOIST_API")
    api: TodoistAPI = TodoistAPI(todoist_apikey)
    api.sync()

    for goal in goals:
        project_name = f'Goals {goal.target_date.year} 🥇'
        project = shared.get_or_create_project(api=api, project_name=project_name)
        if not project:
            continue

        print(project['name'], project['id'])

        section = shared.get_or_create_section(api=api, section_name=goal.category_id, project_id=project['id'])
        if not section:
            continue

        print(section['name'], section['id'])

        label = shared.get_or_create_label(api=api, label_name=goal.priority)
        if not label:
            continue
        
        print(label['name'], label['id'])

        item = shared.add_or_update_task(
            api=api,
            content=f'{goal.name} ({goal.pk})',
            description=goal.rationale,
            project_id=project['id'],
            target_date=goal.target_date,
            section_id=section['id'],
            labels=[label['id'],],
            item_id=goal.task_id
        )
        print(item)

        print(shared.check_task_completed(api, goal.task_id))

if __name__ == "__main__":
    main()
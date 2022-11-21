import os

from dotenv import load_dotenv
from todoist.api import TodoistAPI

from .shared import get_project_by_name, get_label_by_name

TARGET_PROJECTS = ['accountinghub-app', 'gaborschulz-com', 'Kinesis']
LABELS = {
    'Bugfixes': 'bugfixes',
    'In progress': 'in_progress',
    'Up next': 'up_next',
    'Icebox': 'icebox'
}


def main():
    """ MAin function """
    load_dotenv()
    todoist_apikey = os.getenv("TODOIST_API")
    api = TodoistAPI(todoist_apikey)
    api.sync()

    project_ids = []
    for target_project in TARGET_PROJECTS:
        project_ids.append(get_project_by_name(api, target_project))

    label_ids = {}
    for label in LABELS.values():
        label_ids[label] = get_label_by_name(api, label)

    print(project_ids)
    print(label_ids)

    for project_id in project_ids:
        relevant_items = list(
            map(lambda x: x['id'], filter(lambda x: x.data['project_id'] == project_id and x.data['checked'] == 0,  # pylint: disable=cell-var-from-loop
                                          api.state['items'])))
        section_ids = {x['id']: x['name'] for x in
                       filter(lambda x: x.data['project_id'] == project_id, api.state['sections'])}  # pylint: disable=cell-var-from-loop
        for item_id in relevant_items:
            item = api.items.get_by_id(item_id)
            current_labels = item.data['labels']
            labels_to_keep = list(filter(lambda x: x not in label_ids.values(), current_labels))
            if 'section_id' in item.data and item.data['section_id']:
                current_section_name = section_ids.get(item.data['section_id'], None)
                label_to_add = [label_ids.get(LABELS.get(current_section_name))]
                if label_to_add:
                    item.update(labels=labels_to_keep + label_to_add)
                    print(f"{item.data['content']} - {LABELS.get(current_section_name)}")
        api.commit()


if __name__ == '__main__':
    main()

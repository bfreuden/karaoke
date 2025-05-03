import json

from directories import data_dir
from sample_projects import get_or_create_sample_project, get_sample_project_dir


def get_project_data(project_name, sample_project=False):
    if sample_project:
        return get_or_create_sample_project(project_name)
    else:
        with open(f'{data_dir}/{project_name}/_data.json', mode='r') as fp:
            return json.load(fp)

def get_project_dir(project_name, sample_project=False):
    if sample_project:
        return get_sample_project_dir(project_name)
    else:
        return f'{data_dir}/{project_name}'


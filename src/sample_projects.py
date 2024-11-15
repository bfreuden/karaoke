
sample_projects = {
    'dancing_in_the_dark': {
        'youtube_url': 'https://www.youtube.com/watch?v=huMElOuIMmk',
        'genius_url': 'https://genius.com/Amy-macdonald-dancing-in-the-dark-lyrics',
        'language': 'en',
        'model': 'large-v3',
    },
    'ma_direction': {
        'youtube_url': 'https://www.youtube.com/watch?v=Y7-vP7TnluY',
        'genius_url': 'https://genius.com/Sexion-dassaut-ma-direction-lyrics',
        'language': 'fr',
        'model': 'large-v3',
    }
}

from get_or_create_karaoke_project_data import get_project, get_project_dir

def get_sample_project(project_name):
    return get_project(sample_projects[project_name]['youtube_url'])

def get_sample_project_dir(project_name):
    return get_project_dir(get_sample_project(project_name)['youtube_url'])

def get_sample_project_items(project_name, *args):
    project = get_sample_project(project_name)
    return tuple(get_project_dir(project['youtube_url']) if arg == 'project_dir' else project[arg] for arg in args)

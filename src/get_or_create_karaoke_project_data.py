import os
import pickle
import unicodedata
import re
import requests
from bs4 import BeautifulSoup

def get_project_dir(youtube_url, force=False):
    from output_dir import output_dir
    karaoke_project_data = get_or_create_karaoke_project_data(youtube_url, force)
    return f'{output_dir}/{karaoke_project_data["slug"]}'

def get_or_create_karaoke_project_data_from_dict(project_dict, force=False):
    youtube_url = project_dict['youtube_url']
    genius_url = project_dict['genius_url']
    language = project_dict['language']
    model = project_dict['model']
    return get_or_create_karaoke_project_data(youtube_url, genius_url, language, model, force)

def get_or_create_karaoke_project_data(youtube_url, genius_url=None, language=None, model='medium', force=False):
    from output_dir import output_dir
    projects_pickle = f'{output_dir}/projects.pickle'
    if not os.path.exists(projects_pickle):
        projects = {}
    else:
        with open(projects_pickle, 'rb') as file:
            projects = pickle.load(file)
    if youtube_url in projects and not force:
        return projects[youtube_url]
    title = get_youtube_video_title(youtube_url)
    slug = slugify(title)
    project_data = {'title': title, 'slug': slug, 'genius_url': genius_url, 'youtube_url': youtube_url, 'language': language, 'model': model}
    projects[youtube_url] = project_data
    with open(projects_pickle, 'wb') as file:
        pickle.dump(projects, file, protocol=pickle.HIGHEST_PROTOCOL)
    return project_data

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def get_youtube_video_title(youtube_url):
    r = requests.get(youtube_url)
    soup = BeautifulSoup(r.text)
    link = soup.find_all(name="title")[0]
    title = str(link)
    title = title.replace("<title>", "")
    title = title.replace("</title>", "")
    title = title.replace(" - YouTube", "")
    return title


if __name__ == '__main__':
    from sample_projects import dancing_in_the_dark
    karaoke_project_data = get_or_create_karaoke_project_data_from_dict(dancing_in_the_dark, force=True)
    print(f'YouTube URL: {karaoke_project_data["youtube_url"]}')
    print(f'Genius URL: {karaoke_project_data["genius_url"]}')
    print(f'Title: {karaoke_project_data["title"]}')
    print(f'Slug: {karaoke_project_data["slug"]}')
    print(f'Language: {karaoke_project_data["language"]}')

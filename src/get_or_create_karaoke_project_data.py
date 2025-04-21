import json
import os
import re
import unicodedata


def get_project_dir_from_data(project_data):
    from directories import data_dir
    slug = slugify_karaoke(project_data["artist"], project_data["title"])
    return f'{data_dir}/{slug}'

def get_or_create_project_from_data(project_data, force=False, get_only=False):
    from directories import data_dir
    slug = slugify_karaoke(project_data["artist"], project_data["title"])
    project_dir = f"{data_dir}/{slug}"
    if not os.path.exists(project_dir):
        if get_only:
            return None
        os.makedirs(project_dir)
    project_data_json = f'{project_dir}/_data.json'
    if not os.path.exists(project_data_json):
        if get_only:
            return None
        elif not force:
            with open(project_data_json, mode='w') as fp:
                json.dump(project_data, fp, indent=4)
    else:
        with open(project_data_json, mode='r') as fp:
            project_data = json.load(fp)
    return project_data


def slugify_karaoke(artist, title, allow_unicode=False):
    return slugify(f'{artist} {title}', allow_unicode)

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

#
# def get_youtube_video_title(youtube_url):
#     r = requests.get(youtube_url)
#     soup = BeautifulSoup(r.text)
#     link = soup.find_all(name="title")[0]
#     title = str(link)
#     title = title.replace("<title>", "")
#     title = title.replace("</title>", "")
#     title = title.replace(" - YouTube", "")
#     return title
#

if __name__ == '__main__':
    from sample_projects import sample_projects
    project_attributes = sample_projects['dancing_in_the_dark']
    # project_attributes = sample_projects['ma_direction']
    project_data = get_or_create_project_from_data(project_attributes, force=True)
    print(f'YouTube URL: {project_data["youtube_url"]}')
    print(f'Genius URL: {project_data["genius_url"]}')
    print(f'Title: {project_data["title"]}')
    print(f'Slug: {project_data["slug"]}')
    print(f'Language: {project_data["language"]}')

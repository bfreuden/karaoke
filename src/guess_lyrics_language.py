import json
import os
from langdetect import detect

supported_languages = ['en', 'fr', 'ja']

def guess_lyrics_language(lyrics_txt, force=False):
    project_dir = os.path.dirname(lyrics_txt)

    project_data_json = f'{project_dir}/_data.json'
    with open(project_data_json, mode='r') as fp:
        project_data = json.load(fp)

    if 'language' in project_data and not force:
        return project_data["language"]

    with open(lyrics_txt, mode='r') as fp:
        lyrics = fp.read()

    language = guess_language(lyrics, project_data)
    project_data["language"] = language
    with open(project_data_json, mode='w') as fp:
        json.dump(project_data, fp, indent=4)
    return language


def guess_language(lyrics):
    language = detect(lyrics)
    if language not in supported_languages:
        raise Exception(f"Unsupported language: {language}")
    return language


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_name = 'afi-medicate'
    project_dir = get_sample_project_dir(project_name)
    tokens = guess_lyrics_language(f'{project_dir}/lyrics.txt', force=True)
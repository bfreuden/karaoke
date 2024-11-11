import os

import requests
from bs4 import BeautifulSoup

def download_lyrics(genius_url, output_dir, force=False):
    lyrics_txt = f'{output_dir}/lyrics.txt'
    if os.path.exists(lyrics_txt) and not force:
        return lyrics_txt
    r = requests.get(genius_url)
    soup = BeautifulSoup(r.text)
    with open(lyrics_txt, mode="w", encoding="utf-8") as file:
        lyrics_divs = soup.find_all(lambda tag : tag.has_attr('data-lyrics-container'))
        for lyrics_div in lyrics_divs:
            text_nodes = lyrics_div.find_all(text=True)
            for text_node in text_nodes:
                line = str(text_node)
                if not "[" in line:
                    file.write(line)
                    file.write('\n')

if __name__ == '__main__':
    from sample_projects import ma_direction
    from get_or_create_karaoke_project_data import get_project_dir_from_dict, get_or_create_karaoke_project_data_from_dict
    project = ma_direction
    karaoke_project_data = get_or_create_karaoke_project_data_from_dict(project, force=False)
    project_dir = get_project_dir_from_dict(karaoke_project_data)
    download_lyrics(karaoke_project_data["genius_url"], project_dir, force=True)

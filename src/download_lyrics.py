import os

import requests
from bs4 import BeautifulSoup

def download_lyrics(genius_url, output_dir, force=False):
    lyrics_txt = f'{output_dir}/lyrics.txt'
    if os.path.exists(lyrics_txt) and not force:
        return lyrics_txt
    os.makedirs(output_dir)
    r = requests.get(genius_url)
    soup = BeautifulSoup(r.text, "html.parser")
    with open(lyrics_txt, mode="w", encoding="utf-8") as file:
        lyrics_divs = soup.find_all(lambda tag : tag.has_attr('data-lyrics-container'))
        for lyrics_div in lyrics_divs:
            text_nodes = lyrics_div.find_all(string=True)
            for text_node in text_nodes:
                line = str(text_node)
                if not "[" in line:
                    file.write(line)
                    file.write('\n')

if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    project = 'dancing_in_the_dark'
    # project = 'ma_direction'
    project_dir, genius_url = get_sample_project_items(project, 'project_dir', 'genius_url')
    download_lyrics(genius_url, project_dir, force=True)

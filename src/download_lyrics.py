import os
import re

import requests
from bs4 import BeautifulSoup

def download_lyrics(genius_url, output_dir, force=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    lyrics_html = f'{output_dir}/lyrics.html'
    if not os.path.exists(lyrics_html) or force:
        r = requests.get(genius_url)
        lyrics = r.text
        with open(lyrics_html, mode="w", encoding="utf-8") as file:
            file.write(lyrics)
    lyrics_txt = f'{output_dir}/lyrics.txt'
    if os.path.exists(lyrics_txt) and not force:
        return lyrics_txt
    with open(lyrics_html, mode="r", encoding="utf-8") as file:
        lyrics = file.read()
        lyrics = lyrics.replace('\r', '').replace('\n', '')
        lyrics = re.sub('<span[^>]*>', '', lyrics)
        lyrics = lyrics.replace('</span>', '')
        # lyrics = re.sub('<div[^>]*>', '', lyrics)
        # lyrics = lyrics.replace('</div>', '')
        lyrics = re.sub('<a[^>]*>', '', lyrics)
        lyrics = lyrics.replace('</a>', '')
        lyrics = re.sub('<!--[^<]+-->', '', lyrics)
        lyrics = re.sub('<h\\d[^<]+</h\\d>', '', lyrics)
        lyrics = re.sub('<path[^<]+</path>', '', lyrics)
        lyrics = re.sub('<svg[^<]+</svg>', '', lyrics)
        lyrics = re.sub('<button[^<]+</button>', '', lyrics)
        lyrics = re.sub('<div class="LyricsHeader[^<]+</div>', '', lyrics)
        lyrics = re.sub('<div class="SongBioPreview[^<]+</div>', '', lyrics) #
        with open(f'{output_dir}/lyrics-clean.html', mode="w", encoding="utf-8") as html:
            html.write(lyrics)
        soup = BeautifulSoup(lyrics, "html.parser")
        with open(lyrics_txt, mode="w", encoding="utf-8") as file:
            lyrics_divs = soup.find_all(lambda tag : tag.has_attr('data-lyrics-container'))
            for lyrics_div in lyrics_divs:
                text_nodes = lyrics_div.find_all(string=True)
                for text_node in text_nodes:
                    line = str(text_node)
                    if not "[" in line:
                        file.write(line)
                        file.write('\n')
    return lyrics_txt

if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    # project = 'dancing_in_the_dark'
    # project = 'ma_direction'
    project = 'sting_shape_heart'
    project_dir, genius_url = get_sample_project_items(project, 'project_dir', 'genius_url')
    download_lyrics(genius_url, project_dir, force=False)

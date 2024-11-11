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
                file.write(str(text_node))
                file.write('\n')

if __name__ == '__main__':
    from get_or_create_karaoke_project_data import get_project_dir
    youtube_url = 'https://www.youtube.com/watch?v=huMElOuIMmk'
    project_dir = get_project_dir(youtube_url)
    genius_url = 'https://genius.com/Amy-macdonald-dancing-in-the-dark-lyrics'
    download_lyrics(genius_url, project_dir, force=True)


import json
import os
import difflib

import string

def normalize(word, nop=False):
    if nop:
        return word
    else:
        return word.lower().strip(string.punctuation).strip()

def generate_transcript_words(transcript_json, normalize_words=False, force=False):
    output_file = f'{os.path.dirname(transcript_json)}/transcript{"-normalized" if normalize_words else ""}-words.txt'
    if os.path.exists(output_file) and not force:
        return output_file
    with open(transcript_json, mode="r", encoding="utf-8") as file:
        transcript = json.load(file)
    with open(output_file, mode="w", encoding="utf-8") as file:
        for segment in transcript['segments']:
            for word in segment['words']:
                normalized_word = normalize(word["text"], not normalize_words)
                file.write(f'{normalized_word}\n')
    return output_file

def generate_lyrics_words(lyrics_txt, normalize_words=False, force=False):
    output_file = f'{os.path.dirname(lyrics_txt)}/lyrics{"-normalized" if normalize_words else ""}-words.txt'
    if os.path.exists(output_file) and not force:
        return output_file
    with open(lyrics_txt, mode="r", encoding="utf-8") as file:
        lyrics = file.read()
    with open(output_file, mode="w", encoding="utf-8") as file:
        for word in lyrics.split(" "):
            normalized_word = normalize(word, not normalize_words)
            file.write(f'{normalized_word}\n')
    return output_file

def fix_transcript(transcript_json, lyrics_txt, force=False):
    transcript_normalized_words_txt = generate_transcript_words(transcript_json, normalize_words=True, force=force)
    transcript_words_txt = generate_transcript_words(transcript_json, normalize_words=False, force=force)
    lyrics_normalized_words_txt = generate_lyrics_words(lyrics_txt, normalize_words=True, force=force)
    lyrics_words_txt = generate_lyrics_words(lyrics_txt, normalize_words=False, force=force)
    with open(transcript_normalized_words_txt, mode='r', encoding='utf-8') as file:
        transcript_normalized_words = file.readlines()
        transcript_normalized_words = [ word.strip() for word in transcript_normalized_words if len(word.strip()) != 0]
    with open(lyrics_normalized_words_txt, mode='r', encoding='utf-8') as file:
        lyrics_normalized_words = file.readlines()
        lyrics_normalized_words = [word.strip() for word in lyrics_normalized_words if len(word.strip()) != 0]
    # with open(transcript_words_txt, mode='r', encoding='utf-8') as file:
    #     transcript_lines = file.readlines()
    with open(lyrics_words_txt, mode='r', encoding='utf-8') as file:
        lyrics_words = file.readlines()
        lyrics_words = [word.strip() for word in lyrics_words if len(word.strip()) != 0]
    for line in difflib.unified_diff(transcript_normalized_words, lyrics_normalized_words, fromfile='transcript', tofile='lyrics', lineterm='', n=0):
        print(line)

if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('dancing_in_the_dark')
    fix_transcript(f'{project_dir}/transcript.json', f'{project_dir}/lyrics.txt', force=True)

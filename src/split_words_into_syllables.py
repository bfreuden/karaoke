import os.path
import spacy
from spacy_syllables import SpacySyllables

def split_words_into_syllables(lyrics_txt, language, force=False):
    project_dir = os.path.dirname(lyrics_txt)
    output_file = f"{project_dir}/lyrics-syllables.txt"
    if os.path.exists(output_file) and not force:
        return output_file
    if language == "fr":
        model, after = ("fr_core_news_sm", "morphologizer")
    elif language == "en":
        model, after = ("en_core_web_sm", "tagger")
    else:
        raise Exception(f"language not implemented: {language}")

    nlp = spacy.load(model)
    nlp.add_pipe("syllables", after=after)
    with open(lyrics_txt) as fp:
        lyrics = fp.read()
    slash_replacement = "|"
    lyrics_no_slash = lyrics.replace("/", slash_replacement)

    doc = nlp(lyrics)
    last_end = 0
    lyrics_with_syllables = ""
    for token in doc:
        start = token.idx
        end = start + len(token.text)
        if start != last_end:
            lyrics_with_syllables += lyrics[last_end:start]
        last_end = end
        if token._.syllables is None:
            lyrics_with_syllables += token.text
        else:
            if len(token.text) != sum([len(syllable) for syllable in token._.syllables]):
                raise Exception(f"[different length: {token.text}: {token._.syllables}")
            syllable_start = 0
            for syllable in token._.syllables:
                if syllable_start != 0:
                    lyrics_with_syllables += "/"
                syllable_end = syllable_start+len(syllable)
                lyrics_with_syllables += token.text[syllable_start:syllable_end]
                syllable_start = syllable_end
    if last_end != len(lyrics_no_slash):
        lyrics_with_syllables += lyrics[last_end:]
    with open(output_file, mode="w") as fp:
        fp.write(lyrics_with_syllables)
    if lyrics_with_syllables.replace("/", "") != lyrics_no_slash:
        raise Exception("mismatch")
    return output_file

if __name__ == '__main__':
    from sample_projects import get_sample_project_dir, get_or_create_sample_project
    project_name = 'metallica-turn-the-page'
    project_dir = get_sample_project_dir(project_name)
    project_data  = get_or_create_sample_project(project_name)
    split_words_into_syllables( f'{project_dir}/lyrics.txt', project_data['language'], force=True)

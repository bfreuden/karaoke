
import json
import os
import difflib
from itertools import groupby

import spacy
import re

spacy_models = {
    'en': 'en_core_web_sm',
    'fr': 'fr_core_news_sm',
}



def generate_alignment_data_from_lyrics(lyrics_txt, language, force=False):
    alignment_data_lyrics_json = f'{os.path.dirname(lyrics_txt)}/alignment-data-lyrics.json'
    words_lyrics_txt = f'{os.path.dirname(lyrics_txt)}/words-lyrics.txt'
    if os.path.exists(alignment_data_lyrics_json) and os.path.exists(words_lyrics_txt) and not force:
        return alignment_data_lyrics_json, words_lyrics_txt
    nlp = spacy.load(spacy_models[language])
    lyric_segments_data = []
    with open(lyrics_txt, mode="r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line == '':
                continue
            doc = nlp(line)
            words_data = []
            segment_data = {'text': line, 'words': words_data}
            lyric_segments_data.append(segment_data)
            word_data = None
            last_end = -1
            for token in doc:
                if token.pos_ == 'PUNCT' and word_data is not None:
                    # attach to current token
                    spaces = '' if last_end == token.idx else ' ' * (token.idx - last_end)
                    word_data['text'] = f"{word_data['text']}{spaces}{token.text}"
                else:
                    # if token.idx == last_end it is be a multi-token word ("it's" => "it" + "is")
                    if token.idx != last_end:
                        word_data = {
                            'text': '',
                            'lemma': '',
                        }
                        words_data.append(word_data)
                    word_data['text'] = f"{word_data['text']}{token.text}"
                    word_data['lemma'] = f"{word_data['lemma']}{token.lemma_}"
                last_end = token.idx + len(token)
    with open(alignment_data_lyrics_json, mode="w", encoding="utf-8") as output:
        json.dump({'segments': lyric_segments_data}, output, indent = 2, ensure_ascii = False)
    with open(words_lyrics_txt, mode="w", encoding="utf-8") as output:
        for segment_data in lyric_segments_data:
            for word_data in segment_data['words']:
                output.write(word_data['lemma'])
                output.write('\n')
    return alignment_data_lyrics_json, words_lyrics_txt


def generate_alignment_data_from_transcript(transcript_json, language, force=False):
    alignment_data_transcript_json = f'{os.path.dirname(transcript_json)}/alignment-data-transcript.json'
    words_transcript_txt = f'{os.path.dirname(transcript_json)}/words-transcript.txt'
    if os.path.exists(alignment_data_transcript_json) and os.path.exists(words_transcript_txt) and not force:
        return alignment_data_transcript_json, words_transcript_txt
    nlp = spacy.load(spacy_models[language])
    lyrics_segments_data = []
    with open(transcript_json, mode="r", encoding="utf-8") as file:
        transcript = json.load(file)
        for segment in transcript['segments']:
            line = segment['text']
            words = segment['words']
            line = line.strip()
            if line == '':
                continue
            doc = nlp(line)
            words_data = []
            segment_data = {'text': line, 'words': words_data}
            lyrics_segments_data.append(segment_data)
            word_data = None
            last_end = -1
            word_index = 0
            word_offset = 0
            for token in doc:
                word_text = words[word_index]['text']
                assert word_text[word_offset:word_offset+len(token)] == token.text
                word_offset += len(token)
                if token.pos_ == 'PUNCT':
                    # attach to current token
                    word_data['text'] = f"{word_data['text']}{token.text}"
                else:
                    if token.idx != last_end:
                        word_data = {
                            'text': '',
                            'lemma': '',
                            'start': words[word_index]['start'],
                            'end': words[word_index]['end'],
                        }
                        words_data.append(word_data)
                    word_data['text'] = f"{word_data['text']}{token.text}"
                    word_data['lemma'] = f"{word_data['lemma']}{token.lemma_}"
                if word_offset == len(word_text):
                    word_index += 1
                    word_offset = 0
                last_end = token.idx + len(token)
    with open(alignment_data_transcript_json, mode="w", encoding="utf-8") as output:
        json.dump({'segments': lyrics_segments_data}, output, indent = 2, ensure_ascii = False)
    with open(words_transcript_txt, mode="w", encoding="utf-8") as output:
        for segment_data in lyrics_segments_data:
            for word_data in segment_data['words']:
                output.write(word_data['lemma'])
                output.write('\n')
    return alignment_data_transcript_json, words_transcript_txt

def flatten_alignment_data(alignment_data_json):
    output_file = alignment_data_json.replace('alignment-data-', 'alignment-data-flat-')
    flat_words = []
    with open(alignment_data_json, mode="r", encoding="utf-8") as file:
        transcript = json.load(file)
        segment_index = 0
        diff_index = 1
        for segment in transcript['segments']:
            words = segment['words']
            word_index = 0
            for word in words:
                word['segment_index'] = segment_index
                word['word_index'] = word_index
                word['diff_index'] = diff_index
                word_index += 1
                diff_index += 1
                flat_words.append(word)
            segment_index += 1
    with open(output_file, mode="w", encoding="utf-8") as output:
        json.dump(flat_words, output, indent = 2, ensure_ascii = False)
    return output_file


def align_transcript_on_lyrics(transcript_json, lyrics_txt, language, force=False):
    alignment_data_lyrics_json, words_lyrics_txt = generate_alignment_data_from_lyrics(lyrics_txt, language, force)
    alignment_data_transcript_json, words_transcript_txt = generate_alignment_data_from_transcript(transcript_json, language, force)
    flatten_alignment_data_lyrics_json = flatten_alignment_data(alignment_data_lyrics_json)
    flatten_alignment_data_transcript_json = flatten_alignment_data(alignment_data_transcript_json)
    with open(words_lyrics_txt, mode='r', encoding='utf-8') as file:
        lyrics_words = file.readlines()
        lyrics_words = [word.strip() for word in lyrics_words if len(word.strip()) != 0]
    with open(words_transcript_txt, mode='r', encoding='utf-8') as file:
        transcript_words = file.readlines()
        transcript_words = [word.strip() for word in transcript_words if len(word.strip()) != 0]
    with open(flatten_alignment_data_lyrics_json, mode='r', encoding='utf-8') as file:
        flat_alignment_data_lyrics = json.load(file)
    with open(flatten_alignment_data_transcript_json, mode='r', encoding='utf-8') as file:
        flat_alignment_data_transcript = json.load(file)
    skip = 0
    transcript_last_common_line = 1
    transcript_common_line = None
    transcript_next_common_line = None
    transcript_diff_count = None
    lyrics_last_common_line = 1
    lyrics_common_line = None
    lyrics_next_common_line = None
    lyrics_diff_count = None
    transcript_diff_count = 0
    lyrics_diff_count = 0
    transcript_removed = []
    lyrics_added = []
    # https://stackoverflow.com/questions/2307472/generating-and-applying-diffs-in-python
    for line in difflib.unified_diff(transcript_words, lyrics_words, fromfile='transcript', tofile='lyrics', lineterm='', n=0):
        skip += 1
        if skip < 3:
            continue
        match = re.search('@@ -(?P<transcript_line>[0-9]+),?(?P<transcript_count>[0-9]*) \+(?P<lyrics_line>[0-9]+),?(?P<lyrics_count>[0-9]*) @@', line)
        assert match is None and '@@' not in line or match is not None and '@@' in line
        print(line)
        if match is not None:
            transcript_diff_line, transcript_diff_count, transcript_common_line, transcript_next_common_line = diff_positions(match.group('transcript_line'), match.group('transcript_count'))
            lyrics_diff_line, lyrics_diff_count, lyrics_common_line, lyrics_next_common_line = diff_positions(match.group('lyrics_line'), match.group('lyrics_count'))
            transcript_removed.clear()
            lyrics_added.clear()
        else:
            if line.startswith('-'):
                transcript_removed.append(line[1:])
            else:
                lyrics_added.append(line[1:])
            if transcript_diff_count + lyrics_diff_count == len(transcript_removed) + len(lyrics_added):
                # deal with common words by setting timings of transcript on tokens of lyrics
                set_common_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript,
                                                        lyrics_common_line, lyrics_last_common_line, transcript_common_line,
                                                        transcript_last_common_line)
                # deal with diff
                set_diff_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript,
                                                      lyrics_diff_count, lyrics_diff_line, transcript_diff_count,
                                                      transcript_diff_line)

                # continue
                transcript_last_common_line = transcript_next_common_line
                lyrics_last_common_line = lyrics_next_common_line

    transcript_common_line = len(transcript_words)
    lyrics_common_line = len(lyrics_words)

    # deal with last common words by setting timings of transcript on tokens of lyrics
    set_common_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript,
                                            lyrics_common_line, lyrics_last_common_line, transcript_common_line,
                                            transcript_last_common_line)

    # deal with lyrics words that have not been aligned (because the diff contains less words than lyrics)
    set_missing_timings_on_lyrics(flat_alignment_data_lyrics)

    # save fixed transcript
    return save_fixed_transcript(transcript_json, flat_alignment_data_lyrics, alignment_data_lyrics_json)

def set_missing_timings_on_lyrics(flat_alignment_data_lyrics):
    lyrics_segments_with_timings = [list(g) for k, g in
                                    groupby(flat_alignment_data_lyrics, key=lambda x: x['segment_index'])]
    for lyrics_segment_with_timings in lyrics_segments_with_timings:
        previous_word_with_timings = None
        words_without_timings = []
        next_word_with_timings = None
        for i, word in enumerate(lyrics_segment_with_timings):
            if 'start' not in word:
                words_without_timings.append(word)
            else:
                if len(words_without_timings) == 0:
                    # remember it the last word with timing before the words without timings
                    previous_word_with_timings = word
                else:
                    # current word is the first word with timings after the words without timings
                    next_word_with_timings = word
                    set_missing_timings_on_lyrics_segment(flat_alignment_data_lyrics, lyrics_segment_with_timings,
                                                          previous_word_with_timings, words_without_timings, next_word_with_timings)
                    # reset
                    previous_word_with_timings = word
                    words_without_timings.clear()
                    next_word_with_timings = None
        # maybe the last word was missing timings
        if len(words_without_timings) != 0:
            set_missing_timings_on_lyrics_segment(flat_alignment_data_lyrics, lyrics_segment_with_timings, previous_word_with_timings,
                                                  words_without_timings, next_word_with_timings)


def set_linear_timings_on(start, end, words):
    words[0]['start'] = start
    incr = (end-start)/len(words)
    for i in range(len(words)):
        words[i]['start'] = round(start + i*incr, 2)
        words[i]['end'] =  round(start + (i+1)*incr, 2)
        pass
    words[-1]['end'] = end
    pass


def set_missing_timings_on_lyrics_segment(flat_alignment_data_lyrics, lyrics_segment_with_timings,
                                          previous_word_with_timings, words_without_timings, next_word_with_timings):
    if previous_word_with_timings is None and next_word_with_timings is not None:
        # let's insert the words withing the timings of the next word
        start = next_word_with_timings['start']
        end = next_word_with_timings['end']
        set_linear_timings_on(start, end, [*words_without_timings, next_word_with_timings])
    elif next_word_with_timings is None and previous_word_with_timings is not None:
        # let's insert the words withing the timings of the previous word
        start = previous_word_with_timings['start']
        end = previous_word_with_timings['end']
        set_linear_timings_on(start, end, [previous_word_with_timings, *words_without_timings])
    elif next_word_with_timings is not None and previous_word_with_timings is not None:
        # let's insert the words withing the start of the previous word and the end of the next word
        start = previous_word_with_timings['start']
        end = next_word_with_timings['end']
        set_linear_timings_on(start, end, [previous_word_with_timings, *words_without_timings, next_word_with_timings])
    else:
        print("warning, no timings")

def set_diff_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript, lyrics_diff_count,
                                          lyrics_diff_line, transcript_diff_count, transcript_diff_line):
    # the diff is only interesting when there are lyrics words: we just want to set timings on lyrics words
    # because when there are only (removed) transcript words, we'll simply assume the speech-to-text
    # has over-generated random words...
    if lyrics_diff_count > 0:
        nb_words = min(lyrics_diff_count, transcript_diff_count)
        set_nb_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript,
                                            lyrics_diff_line, transcript_diff_line, nb_words)
        # if transcript has 1 more  word (removed) than lyrics, let's assume that the speech to text
        # has split one word into 2, so let's use the end of the second word as the end as
        # the end of the lyrics word
        if transcript_diff_count == lyrics_diff_count + 1:
            # propagate the end of the transcript second word (but not more)
            flat_alignment_data_lyrics[lyrics_diff_line + lyrics_diff_count - 2]['end'] = \
            flat_alignment_data_transcript[transcript_diff_line + transcript_diff_count - 2]['end']
        # if lyrics have more words than transcript, we need to invent new timestamps...
        # but we'll do it at the end


def save_fixed_transcript(transcript_json, flat_alignment_data_lyrics, alignment_data_lyrics_json):
    lyrics_segments_with_timings = [list(g) for k, g in
                                    groupby(flat_alignment_data_lyrics, key=lambda x: x['segment_index'])]
    with open(alignment_data_lyrics_json, mode='r', encoding='utf-8') as file:
        alignment_data_lyrics = json.load(file)
        lyrics_segments = alignment_data_lyrics['segments']
        for words_with_timings, lyrics_segment in zip(lyrics_segments_with_timings, lyrics_segments):
            lyrics_segment['words'] = words_with_timings
            for word_with_timings in words_with_timings:
                for key in ['segment_index', 'word_index', 'diff_index', 'lemma']:
                    del word_with_timings[key]

        output_file = f'{os.path.dirname(transcript_json)}/transcript-fixed.json'
        with open(output_file, mode="w", encoding="utf-8") as output:
            json.dump(alignment_data_lyrics, output, indent=2, ensure_ascii=False)
        return output_file


def set_common_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript,
                                            lyrics_common_line, lyrics_last_common_line, transcript_common_line,
                                            transcript_last_common_line):
    assert transcript_common_line - transcript_last_common_line == lyrics_common_line - lyrics_last_common_line
    if transcript_common_line >= transcript_last_common_line:
        nb_words = transcript_common_line - transcript_last_common_line + 1
        set_nb_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript,
                                            lyrics_last_common_line, transcript_last_common_line, nb_words)


def set_nb_transcript_timings_on_lyrics(flat_alignment_data_lyrics, flat_alignment_data_transcript,
                                        lyrics_from_index, transcript_from_index, nb_words):
    # -1 because diff indices start from 0 instead of 0
    for i in range(-1, nb_words-1):
        flat_alignment_data_lyrics[lyrics_from_index + i]['start'] = \
            flat_alignment_data_transcript[transcript_from_index + i]['start']
        flat_alignment_data_lyrics[lyrics_from_index + i]['end'] = \
            flat_alignment_data_transcript[transcript_from_index + i]['end']


def diff_positions(diff_line_str, diff_count_str):
    diff_line = int(diff_line_str)
    if diff_count_str is None or len(diff_count_str) == 0:
        diff_count = 1
    else:
        diff_count = int(diff_count_str)
    if diff_count == 0:
        common_line = diff_line
        next_common_line = diff_line + 1
    else:
        common_line = diff_line - 1
        next_common_line = diff_line + diff_count
    return diff_line, diff_count, common_line, next_common_line

if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    # project = 'dancing_in_the_dark'
    project = 'ma_direction'
    project_dir, language = get_sample_project_items(project, 'project_dir', 'language')
    align_transcript_on_lyrics(f'{project_dir}/transcript.json', f'{project_dir}/lyrics.txt', language, force=True)

import json
import os.path


def create_segment():
    return {'text': '', 'start': None, 'end': None, 'words': []}

def create_word(text, start, duration):
    return {'text': text, 'start': start, 'end': start + duration}

def add_word_to_segment(segment, word):
    if segment['start'] is None:
        segment['start'] = word['start']
    if len(segment['words']) != 0:
        segment['text'] += ' '
    segment['text'] += word['text']
    segment['end'] = word['end']
    segment['words'].append(word)

def convert_words_ctm_to_transcript(lyrics_txt, words_ctm, force=False):
    project_dir = os.path.abspath(f"{os.path.dirname(words_ctm)}/../../")
    transcript = f'{project_dir}/transcript.json'
    if os.path.exists(transcript) and not force:
        return transcript
    with open(lyrics_txt, mode='r') as file:
        text = file.read().strip()
    # sometimes NeMo refuses to do it:
    # [NeMo I 2025-05-03 12:48:26 data_prep:285] Utterance vocals-mono-075 has too many tokens compared to the audio file duration. Will not generate output alignment files for this utterance.
    if os.path.exists(words_ctm):
        with open(words_ctm, mode='r') as file:
            lines = [line for line in file.readlines() if line.strip() != '']
    else:
        raise Exception("no alignment")
    start = 0
    current_segment = create_segment()
    transcript_data = {
        'text': text,
        'segments': [ current_segment ]
    }
    for line in lines:
        # audio-mono 1 2.40 0.08 A NA lex NA
        [ _, _, start_time, duration, word_text, *_] = line.split(" ")
        index = text.find(word_text, start)
        between = text[start:index]
        if between.strip() != '':
            raise Exception(f'non-whitespace character between 2 words: {between}')
        if '\n' in between:
            current_segment = create_segment()
            transcript_data['segments'].append(current_segment)
        word = create_word(word_text, float(start_time), float(duration))
        add_word_to_segment(current_segment, word)
        start = index + len(word_text)
    with open(transcript, mode='w') as file:
        json.dump(transcript_data, file, indent=4)
    return transcript

if __name__ == '__main__':
    from projects import get_project_dir, get_project_data
    project_name = 'slash-far-and-away'
    project_dir = get_project_dir(project_name)
    convert_words_ctm_to_transcript(f"{project_dir}/lyrics.txt", f"{project_dir}/ctm/words/vocals-no-silence-mono.ctm", force=True)

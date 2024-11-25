
import whisper_timestamped as whisper
import json
import os
from pathlib import Path

def transcribe_speech_to_text(mp3_or_wav, language=None, model_name="medium", initial_prompt = None, force=False):
    project_dir = os.path.dirname(mp3_or_wav)
    output_file = f"{project_dir}/transcript.json"
    if os.path.exists(output_file):
        if force:
            os.remove(output_file)
        else:
            return output_file
    model = load_model(model_name)
    return transcribe_speech_to_text_with_model(mp3_or_wav, output_file, model, language, initial_prompt, force)


def load_model(model_name):
    print(f'Loading model: {model_name}')
    model = whisper.load_model(model_name, device="cpu")
    print(f'done')
    return model


def transcribe_speech_to_text_with_model(mp3_or_wav, output_file, model, language, initial_prompt, force):
    if os.path.exists(output_file):
        if force:
            os.remove(output_file)
        else:
            return output_file
    audio = whisper.load_audio(mp3_or_wav)
    result = whisper.transcribe(model, audio, language=language, initial_prompt=initial_prompt)
    with open(output_file, mode="w", encoding="utf-8") as output:
        json.dump(result, output, indent=2, ensure_ascii=False)


def transcribe_segments_speech_to_text(voice_segments_json, language=None, model_name="medium", initial_prompt = None, force=False):
    project_dir = os.path.dirname(voice_segments_json)
    output_file = f"{project_dir}/transcript.json"
    if os.path.exists(output_file):
        if force:
            os.remove(output_file)
        else:
            return output_file
    model = load_model(model_name)
    output_dir = os.path.dirname(voice_segments_json)
    with open(voice_segments_json, mode='r', encoding='utf-8') as file:
        voice_segments = json.load(file)
    texts = []
    output_segments = []
    for voice_segment in voice_segments['segments']:
        mp3_or_wav = f'{output_dir}/{voice_segment["file"]}'
        voice_segment_start = voice_segment['start']
        transcript_json = Path(mp3_or_wav).with_suffix('.json')
        transcribe_speech_to_text_with_model(mp3_or_wav, transcript_json, model, language=language, initial_prompt=initial_prompt, force=force)
        with open(transcript_json, mode='r', encoding='utf-8') as file:
            transcript = json.load(file)
        texts.append(transcript['text'])
        segments = transcript['segments']
        for segment in segments:
            output_segments.append(segment)
            segment['start'] += voice_segment_start
            segment['end'] += voice_segment_start
            for word in segment['words']:
                word['start'] += voice_segment_start
                word['end'] += voice_segment_start
    with open(output_file, mode="w", encoding="utf-8") as output:
        json.dump({'text': ' '.join(texts), 'segments': output_segments}, output, indent=2, ensure_ascii=False)
    return  output_file

if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    # project_name = 'dancing_in_the_dark'
    project_name = 'ma_direction'
    project_dir, language, model = get_sample_project_items(project_name, 'project_dir', 'language', 'model')

    import time
    track = "audio"
    initial_prompt = None
    # lyrics_txt = f'{project_dir}/lyrics.txt'
    # if lyrics_txt is not None and os.path.exists(lyrics_txt):
    #     with open(lyrics_txt, mode='r', encoding="utf-8") as file:
    #         initial_prompt = file.read()
    #     initial_prompt = f'The input will be a song which official lyrics are:\n\n{initial_prompt}'
    start = time.time()
    # transcript_speech_to_text(f'{project_dir}/{track}.mp3', language=language, model=model, initial_prompt=initial_prompt, force=True)
    transcribe_segments_speech_to_text(f'{project_dir}/voice-segments.json', language=language, model_name=model, initial_prompt=initial_prompt, force=True)
    end = time.time()
    print(f'Elapsed: {end - start}')


import whisper_timestamped as whisper
import json
import os

def transcript_speech_to_text(vocals_mp3, language=None, model="medium", initial_prompt = None, force=False):
    project_dir = os.path.dirname(vocals_mp3)
    output_file = f"{project_dir}/transcript.json"
    if os.path.exists(output_file):
        if force:
            os.remove(output_file)
        else:
            return output_file
    audio = whisper.load_audio(vocals_mp3)
    model = whisper.load_model(model, device="cpu")
    result = whisper.transcribe(model, audio, language=language, initial_prompt=initial_prompt)
    with open(output_file, mode="w", encoding="utf-8") as output:
        json.dump(result, output, indent = 2, ensure_ascii = False)
    return output_file


if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    project_dir, language, model = get_sample_project_items('dancing_in_the_dark', 'project_dir', 'language', 'model')

    import time
    track = "audio"
    initial_prompt = None
    # lyrics_txt = f'{project_dir}/lyrics.txt'
    # if lyrics_txt is not None and os.path.exists(lyrics_txt):
    #     with open(lyrics_txt, mode='r', encoding="utf-8") as file:
    #         initial_prompt = file.read()
    #     initial_prompt = f'The input will be a song which official lyrics are:\n\n{initial_prompt}'
    start = time.time()
    transcript_speech_to_text(f'{project_dir}/{track}.mp3', language=language, model=model, initial_prompt=initial_prompt, force=True)
    end = time.time()
    print(f'Elapsed: {end - start}')

import json
import os
import docker
from docker.types import Mount
from pathlib import Path

def align_lyrics_with_audio(audio_mono_wav_or_list, lyrics_txt_or_list, language, force=False):
    if not isinstance(audio_mono_wav_or_list, list):
        audio_mono_wav_or_list = [audio_mono_wav_or_list]
    if not isinstance(lyrics_txt_or_list, list):
        lyrics_txt_or_list = [lyrics_txt_or_list]
    project_dir = os.path.abspath(os.path.dirname(audio_mono_wav_or_list[0]))
    words_ctm = None
    with open(f'{project_dir}/manifest.json', mode='w') as file:
        for audio_mono_wav, lyrics_txt in zip(audio_mono_wav_or_list, lyrics_txt_or_list):
            words_ctm = os.path.abspath(f"{project_dir}/ctm/words/{Path(os.path.basename(audio_mono_wav)).stem}.ctm")
            if os.path.exists(words_ctm):
                if force:
                    os.remove(words_ctm)
                else:
                    return words_ctm
            with open(lyrics_txt, mode='r') as stream:
                text = stream.read()
            manifest = {  "audio_filepath": f'/input/{os.path.basename(audio_mono_wav)}', "text": text.replace('\n', '|') }
            file.write(json.dumps(manifest))
            file.write('\n')

    if language == 'en' or language == 'ja':
        model_name = 'stt_en_fastconformer_hybrid_large_pc'
    else:
        model_name = f'nvidia/stt_{language}_fastconformer_hybrid_large_pc'
    client = docker.from_env()
    container = client.containers.run(
        'bfreudens/nemo-forced-aligner:2.2.1',
        f'python3 align.py manifest_filepath=/input/manifest.json pretrained_name="{model_name}" additional_segment_grouping_separator="|" output_dir=/input',
        auto_remove=True,
        mounts=[Mount("/input", project_dir, type="bind")],
        detach=True
    )
    output = container.attach(stdout=True, stream=True, logs=True)
    for line in output:
        print(line.decode('utf-8'))
    return words_ctm

if __name__ == '__main__':
    from projects import get_project_dir, get_project_data
    project_name = 'slash-far-and-away'
    project_dir = get_project_dir(project_name)
    language = get_project_data(project_name)['language']
    tokens = align_lyrics_with_audio(f'{project_dir}/vocals-no-silence-mono.wav', f'{project_dir}/lyrics.txt', language, force=True)
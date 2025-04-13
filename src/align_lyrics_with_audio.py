import json
import os
from pathlib import Path
import subprocess
from install import align_py

def align_lyrics_with_audio(audio_mono_wav, lyrics_txt, model, force=False):
    project_dir = os.path.abspath(os.path.dirname(audio_mono_wav))
    words_ctm = os.path.abspath(f"{project_dir}/ctm/words/{Path(os.path.basename(audio_mono_wav)).stem}.ctm")
    if os.path.exists(words_ctm):
        if force:
            os.remove(words_ctm)
        else:
            return words_ctm

    with open(lyrics_txt, mode='r') as stream:
        text = stream.read()
    manifest = {  "audio_filepath": audio_mono_wav, "text": text.replace('\n', '|') }
    with open(f'{project_dir}/manifest.json', mode='w') as file:
        json.dump(manifest, file)

    subprocess.check_call(['karaoke/Scripts/python',  align_py,  f'manifest_filepath={project_dir}/manifest.json',  f'pretrained_name="{model}"',  'additional_segment_grouping_separator="|"', f'output_dir={project_dir}'])
    return words_ctm

if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    project_dir, model = get_sample_project_items('nanana', 'project_dir', 'model')

    tokens = align_lyrics_with_audio(f'{project_dir}/vocals-mono.wav', f'{project_dir}/lyrics.txt', model, force=True)
import os.path
from pathlib import Path


def convert_wav_to_mp3(audio_wav, force=False):
    audio_mp3 =  Path(audio_wav).with_suffix('.mp3')
    if os.path.exists(audio_mp3):
        if force:
            os.remove(audio_mp3)
        else:
            return audio_mp3
    os.system(f'ffmpeg -i {audio_wav} -vn -ar 44100 -ac 2 -b:a 192k {audio_mp3}')
    return audio_mp3

if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('dancing_in_the_dark')
    convert_wav_to_mp3(f'{project_dir}/vocals.wav', force=True)
    convert_wav_to_mp3(f'{project_dir}/accompaniment.wav', force=True)
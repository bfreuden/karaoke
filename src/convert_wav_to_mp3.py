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
    from projects import get_project_dir
    project_dir = get_project_dir('amy-macdonald-dancing-in-the-dark', sample_project=False)
    # convert_wav_to_mp3(f'{project_dir}/audio_\\(Instrumental\\)_model_bs_roformer_ep_317_sdr_12.flac', force=True)
    # convert_wav_to_mp3(f'{project_dir}/vocals.wav', force=True)
    convert_wav_to_mp3(f'{project_dir}/accompaniment.wav', force=True)
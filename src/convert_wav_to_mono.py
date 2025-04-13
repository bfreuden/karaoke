import os.path
from pathlib import Path
from install import ffmpeg

def convert_wav_to_mono(audio_wav, force=False):
    project_dir = os.path.abspath(os.path.dirname(audio_wav))
    audio_mono_wav = os.path.abspath(f"{project_dir}/{Path(os.path.basename(audio_wav)).stem}-mono.wav")
    if os.path.exists(audio_mono_wav):
        if force:
            os.remove(audio_mono_wav)
        else:
            return audio_mono_wav
    os.system(f'{ffmpeg()} -i {audio_wav} -ac 1 {audio_mono_wav}')
    return audio_mono_wav

if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('afi_medicate')
    convert_wav_to_mono(f'{project_dir}/audio.wav', force=True)

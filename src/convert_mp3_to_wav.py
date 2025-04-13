import os.path
from pathlib import Path
from scipy.io import wavfile
from install import ffmpeg

def convert_mp3_to_wav(audio_mp3, sample_rate=None, sample_rate_from_wav=None, force=False):
    if sample_rate is None:
        sample_rate, data = wavfile.read(sample_rate_from_wav)
    audio_wav =  Path(audio_mp3).with_suffix('.wav')
    if os.path.exists(audio_wav):
        if force:
            os.remove(audio_wav)
        else:
            return audio_wav
    os.system(f'{ffmpeg()} -i {audio_mp3} -ar {sample_rate} {audio_wav}')
    return audio_wav

if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_name = 'criminal'
    project_dir = get_sample_project_dir(project_name)
    convert_mp3_to_wav(f'{project_dir}/audio.mp3', sample_rate_from_wav=f'{project_dir}/vocals.wav', force=True)

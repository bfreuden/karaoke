import os

from install import spleeter_pretrained_models
os.environ['MODEL_PATH'] = spleeter_pretrained_models

from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator
from spleeter.audio import Codec
from install import add_ffmpeg_to_path

def split_vocals_and_accompaniment(audio_mp3, force=False):
    project_dir = os.path.dirname(audio_mp3)
    vocals_wav = f"{project_dir}/vocals.wav"
    accompaniment_wav = f"{project_dir}/accompaniment.wav"
    if os.path.exists(vocals_wav) and os.path.exists(accompaniment_wav):
        if force:
            os.remove(vocals_wav)
            os.remove(accompaniment_wav)
        else:
            return (vocals_wav, accompaniment_wav)

    add_ffmpeg_to_path()
    audio_adapter: AudioAdapter = AudioAdapter.get("spleeter.audio.ffmpeg.FFMPEGProcessAudioAdapter")
    separator: Separator = Separator("spleeter:2stems", MWF=False)
    separator.separate_to_file(
        audio_mp3,
        project_dir,
        audio_adapter=audio_adapter,
        offset=0.0,
        duration=600.0,
        codec=Codec.WAV,
        bitrate="128k",
        filename_format="{instrument}.{codec}",
        synchronous=False,
    )
    separator.join()
    return (vocals_wav, accompaniment_wav)


if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    project_dir, = get_sample_project_items('dancing_in_the_dark', 'project_dir')
    vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(f'{project_dir}/audio.mp3', force=True)
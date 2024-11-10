import os

from output_dir import output_dir
pretrained_models = os.path.normpath(f'{output_dir}/pretrained_models')
os.environ['MODEL_PATH'] = pretrained_models

from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator
from spleeter.audio import Codec
from spleeter.model.provider.github import GithubModelProvider

import requests
import tarfile


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

    pretrained_models_2stems = f'{pretrained_models}/2stems'
    # spleeter fails when doing it by itself...
    if not os.path.exists(pretrained_models_2stems):
        os.makedirs(pretrained_models_2stems)
        url = f"https://github.com/deezer/spleeter/releases/download/{GithubModelProvider.LATEST_RELEASE}/2stems.tar.gz"
        response = requests.get(url, stream=True)
        file = tarfile.open(fileobj=response.raw, mode="r|gz")
        file.extractall(path=pretrained_models_2stems)

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
    from output_dir import output_dir
    vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(f'{output_dir}/dancing-in-the-dark/audio.mp3', force=True)
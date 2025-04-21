import os
import docker
from docker.types import Mount


def split_vocals_and_accompaniment(audio_mp3, force=False):
    project_dir = os.path.abspath(os.path.dirname(audio_mp3))
    vocals_wav = os.path.abspath(f"{project_dir}/vocals.wav")
    accompaniment_wav = os.path.abspath(f"{project_dir}/accompaniment.wav")
    if os.path.exists(vocals_wav) and os.path.exists(accompaniment_wav):
        if force:
            os.remove(vocals_wav)
            os.remove(accompaniment_wav)
        else:
            return (vocals_wav, accompaniment_wav)

    client = docker.from_env()
    client.containers.run('bfreudens/spleeter:2.4.2', f'python3 spleet.py --destination /exchange /exchange/{os.path.basename(audio_mp3)}', auto_remove=True, mounts=[Mount("/exchange", project_dir, type="bind")])
    return (vocals_wav, accompaniment_wav)


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('afi-medicate')
    vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(f'{project_dir}/audio.mp3', force=True)
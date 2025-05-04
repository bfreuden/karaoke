import os
import docker
from docker.types import Mount
import shlex

def split_vocals_and_accompaniment(audio_mp3, spleeter=False, force=False):
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
    if spleeter:
        container = client.containers.run(
            'bfreudens/spleeter:2.4.2', f'python3 spleet.py --destination /exchange /exchange/{os.path.basename(audio_mp3)}',
            auto_remove=True,
            mounts=[Mount("/exchange", project_dir, type="bind")],
            detach=True
        )
    else:
        # docker run --rm -it --runtime=nvidia --gpus all  -v audio-separator-models:/tmp/audio-separator-models  -v `pwd`:/workdir beveradb/audio-separator:gpu audio.wav
        container = client.containers.run(
            f'beveradb/audio-separator:gpu', os.path.basename(audio_mp3),
            auto_remove=True,
            runtime="nvidia",
            device_requests=[
                docker.types.DeviceRequest(device_ids=['0'], capabilities=[['gpu']])],
            mounts=[Mount("/workdir", project_dir, type="bind"), Mount("/tmp/audio-separator-models", "audio-separator-models", type="volume")],
            detach=True
        )
    output = container.attach(stdout=True, stream=True, logs=True)
    for line in output:
        print(line.decode('utf-8'))
    if not spleeter:
        instrumental_flac = "audio_(Instrumental)_model_bs_roformer_ep_317_sdr_12.flac"
        if not os.path.exists(f'{project_dir}/{instrumental_flac}'):
            raise Exception(f"missing output file: {instrumental_flac}")
        vocals_flac = "audio_(Vocals)_model_bs_roformer_ep_317_sdr_12.flac"
        if not os.path.exists(f'{project_dir}/{vocals_flac}'):
            raise Exception(f"missing output file: {vocals_flac}")
        os.system(f'ffmpeg -i {project_dir}/{shlex.quote(instrumental_flac)} -ar 44100 {accompaniment_wav}')
        os.system(f'ffmpeg -i {project_dir}/{shlex.quote(vocals_flac)} -ar 44100 {vocals_wav}')

    return (vocals_wav, accompaniment_wav)


if __name__ == '__main__':
    from projects import get_project_dir
    project_dir = get_project_dir('slash-ghost-TODO')
    vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(f'{project_dir}/audio.mp3', spleeter=False, force=True)
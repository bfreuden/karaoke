import os
import docker
from docker.types import Mount
import shlex
import subprocess

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

    if spleeter:
        client = docker.from_env()
        container = client.containers.run(
            'bfreudens/spleeter:2.4.2', f'python3 spleet.py --destination /exchange /exchange/{os.path.basename(audio_mp3)}',
            auto_remove=True,
            mounts=[Mount("/exchange", project_dir, type="bind")],
            detach=True
        )
        output = container.attach(stdout=True, stream=True, logs=True)
        for line in output:
            print(line.decode('utf-8'))
    else:
        # I've not been able to use the GPU (--gpus all) with docker py on Fedora
        # not to mention that it requires to make docker user a unix socket on Fedora :
        #   see: https://superuser.com/questions/1741326/how-to-connect-to-docker-daemon-if-unix-var-run-docker-sock-is-not-available
        my_cmd = f"docker run --rm --runtime=nvidia --gpus all -v audio-separator-models:/tmp/audio-separator-models -v {project_dir}:/workdir beveradb/audio-separator:gpu audio.mp3".split(" ")
        process = subprocess.Popen(my_cmd, stdout=subprocess.PIPE)
        for line in process.stdout:
            print(line.decode('utf-8'))
        process.stdout.close()
        return_code = process.wait()
        if return_code != 0:
            raise Exception()
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
    # for project_name in ["kula-shaker-great-hosannah", "poets-of-the-fall-standstill", "poets-of-the-fall-my-dark-disquiet", "afi-medicate", "amy-macdonald-dancing-in-the-dark", "faouzia-thick-and-thin", "les-fatals-picard-djembe-man", "metallica-turn-the-page", "sexion-dassaut-ma-direction", "slash-back-from-cali"]:
    for project_name in ["kula-shaker-great-hosannah"]:
        project_dir = get_project_dir(project_name)
        vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(f'{project_dir}/audio.mp3', spleeter=False, force=True)
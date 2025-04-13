import requests
import zipfile
import os
import subprocess
import glob
import tarfile
import sys

root_dir = os.path.dirname(os.path.dirname(__file__))
nemo_version = '2.2.1'
nemo_base_dir = f'{root_dir}/NeMo'
nemo_dir = f'{nemo_base_dir}/NeMo-{nemo_version}'
align_py = f'{nemo_dir}/tools/nemo_forced_aligner/align.py'

spleeter_base_dir = f'{root_dir}/spleeter'
spleeter_pretrained_models = f'{spleeter_base_dir}/pretrained_models'

ffmpeg_base_dir = f'{root_dir}/ffmpeg'



def install_nemo():
    r = requests.get(f'https://codeload.github.com/NVIDIA/NeMo/zip/refs/tags/{nemo_version}', allow_redirects=True)
    if not os.path.exists(nemo_base_dir):
        os.makedirs(nemo_base_dir)
    nemo_zip = f'{nemo_base_dir}/{nemo_version}.zip'
    with open(nemo_zip, 'wb') as file:
        file.write(r.content)

    with zipfile.ZipFile(nemo_zip, 'r') as zip_ref:
        zip_ref.extractall(nemo_base_dir)
    os.unlink(nemo_zip)
    if not os.path.exists(align_py):
        raise Exception(f"Can't find NeMo's align.py after download: {align_py}")

    subprocess.check_call([sys.executable, "-m", "pip", "install", '.[asr]'], cwd=nemo_dir)

def install_spleeter():
    pretrained_models_2stems = f'{spleeter_pretrained_models}/2stems'
    if not os.path.exists(pretrained_models_2stems):
        os.makedirs(pretrained_models_2stems)
    url = f"https://github.com/deezer/spleeter/releases/download/v1.4.0/2stems.tar.gz"
    response = requests.get(url, stream=True, allow_redirects=True)
    file = tarfile.open(fileobj=response.raw, mode="r|gz")
    file.extractall(path=pretrained_models_2stems)
    model = f'{pretrained_models_2stems}/checkpoint'
    if not os.path.exists(model):
        raise Exception(f"Can't find Spleeter model after download: {model}")

    subprocess.check_call([sys.executable, "-m", "pip", "install", 'spleeter==2.4.0'], cwd=root_dir)

def ffmpeg():
    if sys.platform.startswith('win'):
        return glob.glob('**/ffmpeg.exe', root_dir=root_dir, recursive=True)[0]
    else:
        return "ffmpeg"

def add_ffmpeg_to_path():
    if sys.platform.startswith('win'):
        os.environ['PATH'] = f'{os.path.dirname(ffmpeg())};{os.environ["PATH"]}'
    pass

def install_ffmpeg():
    if sys.platform.startswith('win'):
        ffmpeg_zip_name = "ffmpeg-release-essentials.zip"
        r = requests.get(f'https://www.gyan.dev/ffmpeg/builds/{ffmpeg_zip_name}', allow_redirects=True)
        if not os.path.exists(ffmpeg_base_dir):
            os.makedirs(ffmpeg_base_dir)
        ffmpeg_zip = f'{ffmpeg_base_dir}/{ffmpeg_zip_name}'
        with open(ffmpeg_zip, 'wb') as file:
            file.write(r.content)
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_base_dir)
        os.unlink(ffmpeg_zip)


if __name__ == '__main__':
    install_ffmpeg()
    install_nemo()
    install_spleeter()
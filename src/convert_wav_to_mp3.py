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
    from output_dir import output_dir
    convert_wav_to_mp3(f'{output_dir}/dancing-in-the-dark/vocals.wav', force=True)
    convert_wav_to_mp3(f'{output_dir}/dancing-in-the-dark/accompaniment.wav', force=True)
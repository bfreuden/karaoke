import json
import os.path

from scipy.io import wavfile


def merge_choirs_in_accompaniment(accompaniment_wav, audio_wav, transcript_json, audio_attenuation_factor = 1.0, force=False):
    output = f'{project_dir}/accompaniment-with-choirs.wav'
    if os.path.exists(output) and not force:
        return output
    accompaniment_sample_rate, accompaniment_samples = wavfile.read(filename=accompaniment_wav)
    audio_sample_rate, audio_samples = wavfile.read(filename=audio_wav)
    with open(transcript_json, mode='r') as fp:
        transcript = json.load(fp)
    if accompaniment_sample_rate != audio_sample_rate:
        raise Exception("different sample rates")
    if len(accompaniment_samples) != len(audio_samples):
        raise Exception("different durations")
    for segment in transcript["segments"]:
        if segment["text"][0] == "(":
            start_sample = int(audio_sample_rate * segment["start"])
            end_sample = int(audio_sample_rate * segment["end"])
            accompaniment_samples[start_sample:end_sample, 0:1] =  (audio_attenuation_factor * audio_samples[start_sample:end_sample, 0:1])
    wavfile.write(
        filename=output,
        rate=accompaniment_sample_rate,
        data=accompaniment_samples
    )
    return output


if __name__ == '__main__':
    from projects import get_project_dir
    project_name = 'hudson-hawk-swinging-on-a-star'
    # project_name = 'afi-medicate' # audio_attenuation_factor = 0.55
    project_dir = get_project_dir(project_name)
    merge_choirs_in_accompaniment(f'{project_dir}/accompaniment.wav', f'{project_dir}/audio.wav', f'{project_dir}/transcript-fixed.json', force=True)

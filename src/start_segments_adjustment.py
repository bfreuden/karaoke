import json
import os
from scipy.io import wavfile

def start_segments_adjustment(transcript_json, split_summary_json, vocals_wav, force=True):
    project_dir = os.path.dirname(transcript_json)
    output_file = f'{project_dir}/segments-adjustment.json'
    if os.path.exists(output_file) and not force:
        return output_file
    # open data
    with open(transcript_json, mode="r") as fp:
        transcript = json.load(fp)
    with open(split_summary_json, mode="r") as fp:
        split_summary = json.load(fp)

    # find the start of vocals
    initial_start = get_initial_start(split_summary, transcript)
    sample_rate, samples = wavfile.read(filename=vocals_wav)
    audio_duration = len(samples)/sample_rate
    segment_adjustment = {
        'sample_rate': sample_rate,
        'audio_duration': audio_duration,
        'nb_samples': len(samples),
        'initial_start': max(0.0, initial_start - 1.0),
        'corrected_segments': [],
        # 'next_suggested_segment': {
        #     'start': transcript['segments'][0]['start'],
        #     'end': transcript['segments'][0]['end'],
        #     'text': transcript['segments'][0]['text'],
        # }
        'next_suggested_segments': [
            {
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'],
            }
            for segment in transcript['segments']
        ]
    }
    with open(output_file, mode="w") as fp:
        json.dump(segment_adjustment, fp, indent=4)
    return output_file


    # avg_word_duration = compute_average_word_duration(transcript)
    #
    # segment = transcript["segments"][segment_index]
    # expected_segment_duration = avg_word_duration * len(transcript["segments"][segment_index]["words"])
    # # so let's say we want twice that number of non-silence in the adjustment context
    #
    #
    # prior_context_seconds = 1.0
    # context = {
    #     "start": 0,
    #     "end": 0,
    #     "segment": {
    #         "start": 0,
    #         "end": 0,
    #     },
    # }
    # # if prev_end > prior_context_seconds:



    pass


def get_initial_start(split_summary, transcript):
    # use the start of the first non-silence
    non_silence_start = split_summary["segments"][0]["start"]
    initial_start = non_silence_start
    transcript_start = transcript["segments"][0]["start"]
    # try to trust the alignment if not too far away (it can be a mistake)
    if initial_start - 2 < transcript_start < initial_start + 2:
        initial_start = min(non_silence_start, transcript_start)
    return initial_start


# def compute_average_word_duration(transcript):
#     avg_word_duration = 0
#     nb_segments = 0
#     for segment in transcript["segments"]:
#         word_duration = (float(segment["end"]) - float(segment["start"])) / len(segment["words"])
#         if 1/word_duration > 7:
#             # more than Eminem... let's say it's a mistake
#             continue
#         nb_segments += 1
#         avg_word_duration += word_duration
#     avg_word_duration /= nb_segments
#     return avg_word_duration


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir

    project_name = 'afi-medicate'
    project_name = 'metallica-turn-the-page'
    project_dir = get_sample_project_dir(project_name)
    start_segments_adjustment(
        f'{project_dir}/transcript.json',
        f'{project_dir}/split-summary.json',
        f'{project_dir}/vocals.wav',
        force=True)

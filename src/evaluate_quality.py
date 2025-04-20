import json
import os
from split_audio import split_audio
from colorama import Fore
from colorama import Style

def evaluate_quality(transcript_json, vocals_wav, force=False):
    project_dir = os.path.dirname(transcript_json)
    output_file = f"{project_dir}/voice-segments.json"
    if os.path.exists(output_file):
        if force:
            os.remove(output_file)
        else:
            return output_file

    voice_segments_json = split_audio(vocals_wav, None, silence_threshold=0.001,
                                      min_silence_length=0.5, split_file=True, force=True)

    with open(transcript_json, mode='r') as fp:
        transcript = json.load(fp)

    with open(voice_segments_json, mode='r') as fp:
        voice_segments = json.load(fp)

    start = int(voice_segments['total']['start'])
    end = int(voice_segments['total']['end'])
    second = 0.0
    print("transcript")
    print("voice segments")
    print("quality")
    line = ""
    increment = 1.0
    while second < end:
        in_transcript = is_in_transcript(transcript, second)
        if in_transcript:
            line += f"{Fore.BLUE}\u2588{Style.RESET_ALL}"
        else:
            line += f"\u2588"
        second += increment
    print(line)
    line = ""
    second = 0.0
    while second < end:
        in_voice_segment = is_in_voice_segment(voice_segments, second)
        if in_voice_segment:
            # silence
            line += f"{Fore.BLUE}\u2588{Style.RESET_ALL}"
        else:
            line += f"\u2588"
        second += increment
    print(line)
    line = ""
    second = 0.0
    # https://mike42.me/blog/2018-06-make-better-cli-progress-bars-with-unicode-block-characters
    while second < end:
        in_transcript = is_in_transcript(transcript, second)
        in_voice_segment = is_in_voice_segment(voice_segments, second)
        if in_transcript:
            if in_voice_segment:
                line += f"{Fore.GREEN}\u2588{Style.RESET_ALL}"
            else:
                # error
                line += f"{Fore.RED}\u2588{Style.RESET_ALL}"
        else:
            if in_voice_segment:
                # silence
                line += f"{Fore.YELLOW}\u2588{Style.RESET_ALL}"
            else:
                line += f"\u2588"
        second += increment
    print(line)
    line = ""
    second = 0.0
    while second < end:
        if int(second) % 10 == 0:
            line += f"{Fore.BLUE}\u2588{Style.RESET_ALL}"
        else:
            line += f"\u2588"
        second += increment
    print(line)


def is_in_transcript(transcript, second):
    for segment in transcript['segments']:
        if segment['start'] > second:
            break
        # if segment['start'] <= second <= segment['end']:
        #     return True
        for word in segment['words']:
            if word['start'] > second:
                break
            if word['start'] <= second <= word['end']:
                return True
    return False

def is_in_voice_segment(transcript, second):
    for segment in transcript['segments']:
        if segment['start'] > second:
            break
        if segment['start'] <= second <= segment['end']:
            return True
    return False


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir

    # project_name = 'dancing_in_the_dark'
    # project_name = 'ma_direction'
    # project_name = 'afi_medicate'
    project_name = 'frieren_hareru'
    project_dir = get_sample_project_dir(project_name)
    evaluate_quality(f'{project_dir}/transcript.json', f'{project_dir}/vocals.wav', force=True)


import json
import os.path
import time
import math


def convert_transcript_to_segments_ass(transcript_json, force=False):
    from directories import resources_dir
    header_ass = f'{resources_dir}/header.ass'
    segments_ass = f'{os.path.dirname(transcript_json)}/subtitles-segments.ass'
    if os.path.exists(segments_ass) and not force:
        return
    with open(transcript_json, mode='r', encoding='utf-8') as file:
        transcript = json.load(file)

    with open(segments_ass, mode='w', encoding='utf-8') as ass:
        # write header
        with open(header_ass, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                ass.write(line.rstrip())
                ass.write('\n')
        # write lyrics
        for segment in transcript['segments']:
            text = segment['text']
            start = segment['words'][0]['start']
            start_str = ass_time(start)
            end = segment['words'][-1]['end']
            end_str = ass_time(end)
            ass.write(f'Dialogue: 0,{start_str},{end_str},Sample KM [Up],,0,0,0,,{text}\n')

def ass_time(seconds):
    cents = round(100*(seconds - math.floor(seconds)))
    cents_str = "{:02d}".format(cents)
    hmsm = time.strftime('%H:%M:%S', time.gmtime(math.floor(seconds)))
    return f'{hmsm[1:]}.{cents_str}'


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('dancing_in_the_dark')
    convert_transcript_to_segments_ass(f'{project_dir}/transcript-fixed.json', force=True)

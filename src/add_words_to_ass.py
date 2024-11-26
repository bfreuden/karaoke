import json
import os.path
import time
import math


def convert_transcript_to_words_ass(subtitles_segments_ass, transcript_json, force=False):
    output_file = f'{os.path.dirname(transcript_json)}/subtitles-words.ass'
    if os.path.exists(output_file) and not force:
        return
    with open(transcript_json, mode='r', encoding='utf-8') as file:
        transcript = json.load(file)
    transcript_segments = transcript['segments']
    line_index = 0
    with open(output_file, mode='w', encoding='utf-8') as ass:
        with open(subtitles_segments_ass, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                line = line.rstrip()
                if not line.startswith('Dialogue'):
                    ass.write(line)
                    ass.write('\n')
                else:
                    index = line.find('0,0,0,,')
                    index += 7
                    start_line = line[0:index]
                    text = line[index:]
                    ass.write(start_line)
                    transcript_segment = transcript_segments[line_index]
                    start_from = 0
                    for word in transcript_segment['words']:
                        # FIXME!!
                        try:
                            start = word['start']
                            end = word['end']
                            word_duration_cents = round(100 * (end - start))
                            ass.write('{\\k')
                            ass.write(str(word_duration_cents))
                            ass.write('}')
                        except:
                            print(f"no timing on word: {word['text']}")
                        ass.write(word['text'])
                        ass.write(' ')
                    ass.write('\n')
                    line_index += 1
        # # write lyrics
        # for segment in transcript['segments']:
        #     text = segment['text']
        #     start = segment['words'][0]['start']
        #     start_str = ass_time(start)
        #     end = segment['words'][-1]['end']
        #     end_str = ass_time(end)
        #     ass.write(f'Dialogue: 0,{start_str},{end_str},Sample KM [Up],,0,0,0,,{text}\n')
    return output_file

def ass_time(seconds):
    cents = round(100*(seconds - math.floor(seconds)))
    cents_str = "{:02d}".format(cents)
    hmsm = time.strftime('%H:%M:%S', time.gmtime(math.floor(seconds)))
    return f'{hmsm[1:]}.{cents_str}'


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    # project_name = 'dancing_in_the_dark'
    # project_name = 'ma_direction'
    project_name = 'criminal'
    project_dir = get_sample_project_dir(project_name)
    convert_transcript_to_words_ass(f'{project_dir}/subtitles-segments.ass', f'{project_dir}/transcript-fixed.json', force=True)

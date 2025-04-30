import json
import os.path
import time
import math


def add_words_to_segments_ass(subtitles_segments_ass, transcript_json, force=False):
    fixed = "-fixed" if "-fixed" in transcript_json else ""
    output_file = f'{os.path.dirname(transcript_json)}/subtitles-words{fixed}.ass'
    if os.path.exists(output_file) and not force:
        return output_file
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
                    #text = line[index:]
                    ass.write(start_line)
                    transcript_segment = transcript_segments[line_index]
                    nb_words = len(transcript_segment['words'])
                    for i in range(0, nb_words - 1):
                        word = transcript_segment['words'][i]
                        start = word['start']
                        end = transcript_segment['words'][i+1]['start']
                        word_duration_cents = round(100 * (end - start))
                        ass.write('{\\k')
                        ass.write(str(word_duration_cents))
                        ass.write('}')
                        ass.write(word['text'])
                        ass.write(' ')
                    word = transcript_segment['words'][-1]
                    start = word['start']
                    end = word['end']
                    word_duration_cents = round(100 * (end - start))
                    ass.write('{\\k')
                    ass.write(str(word_duration_cents))
                    ass.write('}')
                    ass.write(word['text'])


                    ass.write('\n')
                    line_index += 1
    return output_file

def ass_time(seconds):
    cents = round(100*(seconds - math.floor(seconds)))
    cents_str = "{:02d}".format(cents)
    hmsm = time.strftime('%H:%M:%S', time.gmtime(math.floor(seconds)))
    return f'{hmsm[1:]}.{cents_str}'


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_name = 'afi-medicate'
    project_dir = get_sample_project_dir(project_name)
    add_words_to_segments_ass(f'{project_dir}/subtitles-segments.ass', f'{project_dir}/transcript.json', force=True)

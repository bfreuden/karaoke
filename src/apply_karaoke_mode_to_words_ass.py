import json
import os.path
import re
import time
import math


def apply_karaoke_mode_to_words_ass(words_ass, force=False):
    fixed = "-fixed" if "-fixed" in words_ass else ""
    output_file = f'{os.path.dirname(words_ass)}/subtitles-words-karaoke{fixed}.ass'
    if os.path.exists(output_file) and not force:
        return output_file
    with open(output_file, mode='w', encoding='utf-8') as ass:
        dialogue_lines = []
        with open(words_ass, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                line = line.rstrip()
                if not line.startswith('Dialogue'):
                    ass.write(line)
                    ass.write('\n')
                else:
                    dialogue_lines.append(line)

        dialogue_lines = [line for line in dialogue_lines if line.strip() != '']
        new_dialog_lines = []
        for dialogue_line in dialogue_lines:
            match = re.match("Dialogue: (?P<prefix>[^,]+,)(?P<start>[^,]+),(?P<end>[^,]+),(?P<sample>Sample KM \[Up],,0,0,0,),(?P<segment>.*)", dialogue_line)
            prefix = match['prefix']
            start = match['start']
            end = match['end']
            sample = match['sample']
            segment = match['segment']
            ass.write(f"Comment: {prefix}{start},{end}{sample}karaoke,{segment}")
            ass.write('\n')
            effect = "{\\k90\\fad(300,200)}"
            new_dialog_lines.append(f"Dialogue: {prefix}{shift_ass_time(start, -0.9)},{shift_ass_time(end, 0.2)},{sample}fx,{effect}{segment}")
        for new_dialog_line in new_dialog_lines:
            ass.write(new_dialog_line)
            ass.write('\n')
        ass.write('\n')
    return output_file

def shift_ass_time(the_ass_time, shift):
    return ass_time(parse_ass_time(the_ass_time) + shift)

def parse_ass_time(the_ass_time):
    match = re.match("(?P<h>\\d):(?P<m>\\d\\d):(?P<s>\\d\\d)\.(?P<cents>\\d\\d)", the_ass_time)
    h = int(match['h'])
    m = int(match['m'])
    s = int(match['s'])
    cents = int(match['cents'])
    seconds = 3600*h + 60*m + s + cents/100
    return seconds

def ass_time(seconds):
    cents = round(100*(seconds - math.floor(seconds)))
    cents_str = "{:02d}".format(cents)
    hmsm = time.strftime('%H:%M:%S', time.gmtime(math.floor(seconds)))
    return f'{hmsm[1:]}.{cents_str}'


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_name = 'afi-medicate'
    project_dir = get_sample_project_dir(project_name)
    apply_karaoke_mode_to_words_ass(f'{project_dir}/subtitles-words.ass', force=True)

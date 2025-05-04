import json
import os
import re


def insert_silences_in_alignment(words_no_silence_ctm, split_summary_json, force=False):
    project_dir = os.path.abspath(os.path.dirname(words_no_silence_ctm))
    words_with_silence_ctm = os.path.abspath(f"{project_dir}/{os.path.basename(words_no_silence_ctm).replace('no-silence', 'with-silence')}")
    if words_with_silence_ctm == words_no_silence_ctm:
        raise Exception("bug")
    if os.path.exists(words_with_silence_ctm):
        if force:
            os.remove(words_with_silence_ctm)
        else:
            return words_with_silence_ctm
    with open(split_summary_json, mode='r') as fp:
        split_summary = json.load(fp)
    silence_cuts = split_summary['silence_cuts']
    with open(words_no_silence_ctm, mode='r') as fp:
        lines = fp.readlines()
    with open(words_with_silence_ctm, mode='w') as fp:
        for line in lines:
            if line.strip() == '':
                fp.write(line)
                continue
            # vocals-no-silence-mono 1 4.72 0.08 could NA lex NA
            match = re.match('^([^ ]+ \\d+ )(\\d+\\.\\d+)(.+)$', line)
            prefix = match.group(1)
            start = float(match.group(2))
            suffix = match.group(3)
            new_start = start
            for silence_cut in silence_cuts:
                at = silence_cut['at']
                if at < start:
                    new_start += silence_cut['removed']
                else:
                    break
            fp.write(f'{prefix}{new_start:.2f}{suffix}\n')
    return words_with_silence_ctm


if __name__ == '__main__':
    from projects import get_project_dir
    project_name = 'slash-far-and-away'
    project_dir = get_project_dir(project_name)
    insert_silences_in_alignment(f'{project_dir}/ctm/words/vocals-no-silence-mono.ctm', f'{project_dir}/split-summary.json', force=True)

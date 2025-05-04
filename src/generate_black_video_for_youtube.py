import os.path
import tempfile
import re

def generate_black_video_for_youtube(subtitles_ass, audio_mp3, font_size=24, margin_v=120, pitch_adjustment_semitones= None, force=False):
    project_dir = os.path.abspath(os.path.dirname(subtitles_ass))
    video_karaoke_black_mp4 = os.path.abspath(f"{project_dir}/video-karaoke-black.mp4")
    if os.path.exists(video_karaoke_black_mp4):
        if force:
            os.remove(video_karaoke_black_mp4)
        else:
            return video_karaoke_black_mp4
    with open(subtitles_ass, mode='r') as fp:
        content = fp.read()
        modified_content = content
        backslash = "\\"
        if margin_v is not None or font_size is not None:
            modified_content = re.sub("(Style: Sample KM \[Up],Arial),([0-9]+),(&H00008AFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.5,0,8,2,2),([0-9]+),(1)", f"\\1,{f'{backslash}2' if font_size is None else font_size},\\3,{f'{backslash}4' if margin_v is None else margin_v},\\5", content)
    with tempfile.NamedTemporaryFile() as tmp:
        with open(tmp.name, mode='w') as fp:
            fp.write(modified_content)
        pitch_adjustment_options = "" # not tested
        if pitch_adjustment_semitones is not None:
            if pitch_adjustment_semitones > 0:
                frequency_factor = 1.059463035 ** pitch_adjustment_semitones
            else:
                frequency_factor = 1.059463035 ** (1.0/pitch_adjustment_semitones)
            pitch_adjustment_options = f'-af asetrate=44100*{frequency_factor},aresample=44100,atempo=1/{frequency_factor}'

        mp3_conversion_options = "-vn -ar 44100 -ac 2 -b:a 192k" if audio_mp3.endswith(".wav") else ""  # not tested
        os.system(f'ffmpeg -f lavfi -i color=c=black:s=1920x1080:r=5  -filter_complex ass={tmp.name}  -i {audio_mp3} {pitch_adjustment_options} -crf 0 -c:a copy {mp3_conversion_options} -c:v libx264 -crf 23 -preset fast -shortest {video_karaoke_black_mp4}')

    return video_karaoke_black_mp4

if __name__ == '__main__':
    from projects import get_project_dir
    # for project_name in ["kula-shaker-great-hosannah", "poets-of-the-fall-standstill", "poets-of-the-fall-my-dark-disquiet", "afi-medicate", "amy-macdonald-dancing-in-the-dark", "faouzia-thick-and-thin", "les-fatals-picard-djembe-man", "metallica-turn-the-page", "sexion-dassaut-ma-direction", "slash-back-from-cali"]:
    for project_name in ["naheulband-nanana-de-lelfe"]:
        project_dir = get_project_dir(project_name)
        # generate_black_video_for_youtube(f'{project_dir}/subtitles-words-karaoke.ass', f'{project_dir}/accompaniment.mp3', force=True)
        generate_black_video_for_youtube(f'{project_dir}/subtitles-words-karaoke-fixed.ass', f'{project_dir}/accompaniment.mp3', force=True)

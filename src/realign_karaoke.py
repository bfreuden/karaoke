import json
import traceback

from convert_transcript_to_ass import convert_transcript_to_segments_ass
from add_words_to_segments_ass import add_words_to_segments_ass
from apply_karaoke_mode_to_words_ass import apply_karaoke_mode_to_words_ass
from convert_wav_to_mono import convert_wav_to_mono
from get_or_create_karaoke_project_data import get_or_create_project_from_data, get_project_dir_from_data
from progress_notifier import PrintProgressNotifier
from realign_words_in_corrected_segments import realign_words_in_corrected_segments
from create_media_links import create_media_links_for_realign

STEPS = 7

def realign_karaoke(project_dir, progress=PrintProgressNotifier(STEPS), force=False):
    try:
        # default values
        default_speech_to_text_target = 'vocals'
        # default_voice_threshold = 0.001
        # default_min_silence_length = 0.45
        progress.notify("Reading project data")
        with open(f'{project_dir}/_data.json', mode='r') as fp:
            project_data = json.load(fp)

        language = project_data['language']

        progress.notify("Converting wav to mono")
        convert_wav_to_mono(f'{project_dir}/vocals.wav', force=True)

        progress.notify("Realigning words")
        transcript_json = realign_words_in_corrected_segments(
            f'{project_dir}/transcript-fixed.json',
            f'{project_dir}/vocals-mono.wav',
            None,  # f'{project_dir}/lyrics-syllables.txt',
            language,
            force=True
        )

        progress.notify(f"Converting transcript to segments ass")
        subtitles_segments_ass = convert_transcript_to_segments_ass(transcript_json, force=True)

        progress.notify(f"Converting transcript to words ass")
        subtitles_words_ass = add_words_to_segments_ass(subtitles_segments_ass, transcript_json, force=True)

        progress.notify(f"Applying karaoke mode to words ass")
        subtitles_karaoke_ass = apply_karaoke_mode_to_words_ass(subtitles_words_ass, force=True)

        progress.notify(f"Creating media links")
        video_mp4 = f'{project_dir}/video.mp4'
        video_accompaniment_mp4 = f'{project_dir}/video-accompaniment.mp4'
        create_media_links_for_realign(project_data, video_mp4, video_accompaniment_mp4, subtitles_karaoke_ass, force=force)

    except:
        print(traceback.format_exc())


if __name__ == '__main__':

    from sample_projects import sample_projects, get_or_create_sample_project
    # project_names = sample_projects.keys()

    project_names = [ 'metallica-turn-the-page' ]

    # https://pypi.org/project/eng-syl/
    # https://github.com/Kozea/Pyphen
    # https://spacy.io/universe/project/spacy_syllables

    for project_name in project_names:
        try:
            project_data = get_or_create_sample_project(project_name)

            print("-- Creating project")
            get_or_create_project_from_data(project_data, force=False)
            project_dir = get_project_dir_from_data(project_data)

            force = False
            realign_karaoke(project_dir, force=force)

        except:
            print(traceback.format_exc())

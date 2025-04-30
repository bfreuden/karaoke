import json
import os
import traceback

from convert_wav_to_mp3 import convert_wav_to_mp3
from download_lyrics import download_lyrics
from guess_lyrics_language import guess_lyrics_language
from download_youtube_video import download_youtube_video
from extract_mp3_from_mp4 import extract_mp3_from_mp4
from get_or_create_karaoke_project_data import get_or_create_project_from_data, get_project_dir_from_data
from split_vocals_and_accompaniment_docker import split_vocals_and_accompaniment
from convert_mp3_to_wav import convert_mp3_to_wav
from convert_wav_to_mono import convert_wav_to_mono
from align_lyrics_with_audio_docker import align_lyrics_with_audio
from convert_words_ctm_to_transcript import convert_words_ctm_to_transcript
from convert_transcript_to_ass import convert_transcript_to_segments_ass
from add_words_to_segments_ass import add_words_to_segments_ass
from apply_karaoke_mode_to_words_ass import apply_karaoke_mode_to_words_ass
from replace_audio_track_in_video import replace_audio_track_in_video
from split_words_into_syllables import split_words_into_syllables
# from insert_subtitles_in_video import insert_subtitles_in_video
# from evaluate_quality import evaluate_quality
from insert_silences_in_alignment import insert_silences_in_alignment
from progress_notifier import PrintProgressNotifier
from split_audio import split_audio
from create_media_links import create_media_links

# from align_transcript_on_lyrics import align_transcript_on_lyrics
# from split_audio import split_audio
# from transcribe_speech_to_text import transcribe_segments_speech_to_text
# from fix_segment_start_end_timings import fix_segment_start_end_timings

STEPS = 19

def generate_karaoke(project_dir, progress=PrintProgressNotifier(STEPS), force=False):
    try:
        # default values
        default_speech_to_text_target = 'vocals'
        # default_voice_threshold = 0.001
        # default_min_silence_length = 0.45
        progress.notify("Reading project data")
        with open(f'{project_dir}/_data.json', mode='r') as fp:
            project_data = json.load(fp)

        youtube_url = project_data['youtube_url']
        genius_url = project_data['genius_url']
        language = project_data['language']

        speech_to_text_target = project_data[
            'speech_to_text_target'] if 'speech_to_text_target' in project_data else default_speech_to_text_target
        # min_silence_length = karaoke_project_data[
        #     'min_silence_length'] if 'min_silence_length' in karaoke_project_data else default_min_silence_length
        # silence_threshold = karaoke_project_data[
        #     'silence_threshold'] if 'silence_threshold' in karaoke_project_data else default_voice_threshold

        progress.notify("Downloading YouTube video")
        video_mp4 = download_youtube_video(youtube_url, project_dir, force=force)

        progress.notify("Downloading lyrics")
        lyrics_txt = download_lyrics(genius_url, project_dir, force=force)

        progress.notify("Splitting words into syllables")
        lyrics_syllables_txt = split_words_into_syllables(lyrics_txt, language, force=force)

        progress.notify("Guessing lyrics language")
        language = guess_lyrics_language(lyrics_txt, force=False)

        progress.notify("Extracting audio from video")
        audio_mp3 = extract_mp3_from_mp4(video_mp4, force=force)

        progress.notify("Splitting audio track in vocals and accompaniment")
        vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(audio_mp3, force=force)

        progress.notify("Converting audio track to wav")
        audio_wav = convert_mp3_to_wav(audio_mp3, sample_rate_from_wav=vocals_wav, force=force)

        progress.notify("Converting vocals track to mp3")
        vocals_mp3 = convert_wav_to_mp3(vocals_wav, force=force)

        progress.notify("Converting accompaniment track to mp3")
        accompaniment_mp3 = convert_wav_to_mp3(accompaniment_wav, force=force)

        progress.notify(f"Removing long silences from {speech_to_text_target}")
        split_summary_json, no_silence_filename = split_audio(audio_wav if speech_to_text_target == 'audio' else vocals_wav,
                                                              None, silence_threshold=0.001, remove_silences=True,
                                                              min_silence_length=0.5, split_file=True, force=force)

        progress.notify(f"Converting {no_silence_filename} to mono")
        mono_wav = convert_wav_to_mono(no_silence_filename, force=force)

        progress.notify(f"Aligning lyrics with {speech_to_text_target} ({mono_wav})")
        condensed_words_ctm = align_lyrics_with_audio(mono_wav, lyrics_txt, language, force=force)

        progress.notify(f"Inserting silences back into {speech_to_text_target} alignment data")
        words_ctm = insert_silences_in_alignment(condensed_words_ctm, split_summary_json, force=force)

        progress.notify(f"Converting alignment to transcript")
        transcript_json = convert_words_ctm_to_transcript(lyrics_txt, words_ctm, force=force)

        progress.notify(f"Converting transcript to segments ass")
        subtitles_segments_ass = convert_transcript_to_segments_ass(transcript_json, force=force)

        progress.notify(f"Converting transcript to words ass")
        subtitles_words_ass = add_words_to_segments_ass(subtitles_segments_ass, transcript_json, force=force)

        progress.notify(f"Applying karaoke mode to words ass")
        subtitles_karaoke_ass = apply_karaoke_mode_to_words_ass(subtitles_words_ass, force=force)

        progress.notify(f"Replacing audio track in video")
        video_accompaniment_mp4 = replace_audio_track_in_video(video_mp4, accompaniment_mp3, force=force)

        progress.notify(f"Creating media links")
        create_media_links(project_data, video_mp4, video_accompaniment_mp4, subtitles_karaoke_ass, force=force)

        # progress.notify(f"Converting vocals to mono")
        # mono_wav = convert_wav_to_mono(vocals_wav, force=force)


        # progress.notify(f"Inserting subtitles in video")
        # video_karaoke_mp4 = insert_subtitles_in_video(video_accompaniment_mp4, subtitles_karaoke_ass, force=True)

        # progress.notify(f"Showing quality report {project_name}")
        # evaluate_quality(vocals_wav, transcript_json)

    except:
        print(traceback.format_exc())
    # progress.notify(f"Splitting {speech_to_text_target} track based on vocals silences")
    # target_filename = None if speech_to_text_target == 'vocals' else audio_wav
    # voice_segments_json = split_audio(vocals_wav, target_filename=target_filename, silence_threshold=silence_threshold, min_silence_length=min_silence_length, force=force)
    # progress.notify(f"Running speech to text on {speech_to_text_target} track")
    # transcript_json = transcribe_segments_speech_to_text(voice_segments_json, language=language, model_name=model_name, initial_prompt=default_initial_prompt, force=force)
    # progress.notify("Aligning transcription on official lyrics")
    # aligned_transcript_json = align_transcript_on_lyrics(transcript_json, lyrics_txt, language, force=force)
    # progress.notify("Generating subtitles")
    # convert_transcript_to_segments_ass(aligned_transcript_json)


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
            generate_karaoke(project_dir, force=force)

        except:
            print(traceback.format_exc())

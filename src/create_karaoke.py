import os
import traceback
import shutil

from convert_wav_to_mp3 import convert_wav_to_mp3
from download_lyrics import download_lyrics
from download_youtube_video import download_youtube_video
from extract_mp3_from_mp4 import extract_mp3_from_mp4
from get_or_create_karaoke_project_data import get_or_create_project_from_attributes
from split_vocals_and_accompaniment_docker import split_vocals_and_accompaniment
from src.convert_mp3_to_wav import convert_mp3_to_wav
from convert_wav_to_mono import convert_wav_to_mono
from align_lyrics_with_audio_docker import align_lyrics_with_audio
from convert_words_ctm_to_transcript import convert_words_ctm_to_transcript
from convert_transcript_to_ass import convert_transcript_to_segments_ass
from add_words_to_segments_ass import add_words_to_segments_ass
from apply_karaoke_mode_to_words_ass import apply_karaoke_mode_to_words_ass
from replace_audio_track_in_video import replace_audio_track_in_video
from insert_subtitles_in_video import insert_subtitles_in_video
from src.evaluate_quality import evaluate_quality
from src.insert_silences_in_alignment import insert_silences_in_alignment
from src.split_audio import split_audio

# from src.align_transcript_on_lyrics import align_transcript_on_lyrics
# from src.split_audio import split_audio
# from src.transcribe_speech_to_text import transcribe_segments_speech_to_text
# from fix_segment_start_end_timings import fix_segment_start_end_timings

if __name__ == '__main__':

    from sample_projects import sample_projects, get_sample_project_dir
    # project_name = [ 'dancing_in_the_dark' ]
    # project_name = [ 'afi_17_crimes' ]
    # project_name = [ 'afi_medicate' ]
    # project_names = [ 'frieren_hareru' ]
    # project_name = [ 'faouzia_thick_thin' ]
    # project_name = [ 'poets_standstill' ]
    # project_name = [ 'sting_shape_heart' ]
    # project_name = [ 'nanana' ]
    # project_name = [ 'ma_direction' ]
    # project_name = [ 'criminal' ]
    project_names = sample_projects.keys()

    for project_name in project_names:
        try:
            project_attributes = sample_projects[project_name]
            force = False

            # default values
            default_voice_threshold = 0.001
            default_model_name = 'stt_en_fastconformer_hybrid_large_pc'
            default_speech_to_text_target = 'vocals'
            default_min_silence_length = 0.45
            default_initial_prompt = None

            print("-- Creating project data")
            karaoke_project_data = get_or_create_project_from_attributes(project_attributes, force=True)

            youtube_url = karaoke_project_data['youtube_url']
            genius_url = karaoke_project_data['genius_url']
            slug = karaoke_project_data['slug']
            model = karaoke_project_data['model']
            language = karaoke_project_data['language']
            model_name = karaoke_project_data['model'] if 'model' in karaoke_project_data else default_model_name
            speech_to_text_target = karaoke_project_data['speech_to_text_target'] if 'speech_to_text_target' in karaoke_project_data else default_speech_to_text_target
            min_silence_length = karaoke_project_data['min_silence_length'] if 'min_silence_length' in karaoke_project_data else default_min_silence_length
            silence_threshold = karaoke_project_data['silence_threshold'] if 'silence_threshold' in karaoke_project_data else default_voice_threshold
            project_dir = get_sample_project_dir(project_name)

            print("-- Downloading YouTube video")
            video_mp4 = download_youtube_video(youtube_url, project_dir, force=force)

            print("-- Downloading lyrics")
            lyrics_txt = download_lyrics(genius_url, project_dir, force=force)

            print("-- Extracting audio from video")
            audio_mp3 = extract_mp3_from_mp4(video_mp4, force=force)

            print("-- Splitting audio track in vocals and accompaniment")
            vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(audio_mp3, force=force)

            print("-- Converting audio track to wav")
            audio_wav = convert_mp3_to_wav(audio_mp3, sample_rate_from_wav=vocals_wav, force=force)

            print("-- Converting vocals track to mp3")
            vocals_mp3 = convert_wav_to_mp3(vocals_wav, force=force)

            print("-- Converting accompaniment track to mp3")
            accompaniment_mp3 = convert_wav_to_mp3(accompaniment_wav, force=force)

            print(f"-- Removing long silences from {speech_to_text_target}")
            split_summary_json, no_silence_filename = split_audio(audio_wav if speech_to_text_target == 'audio' else vocals_wav, None, silence_threshold=0.001, remove_silences=True, min_silence_length=0.5, split_file=True, force=force)

            print(f"-- Converting {no_silence_filename} to mono")
            mono_wav = convert_wav_to_mono(no_silence_filename, force=force)

            print(f"-- Aligning lyrics with {speech_to_text_target} ({mono_wav})")
            condensed_words_ctm = align_lyrics_with_audio(mono_wav, lyrics_txt, model, force=force)

            print(f"-- Inserting silences back into {speech_to_text_target} alignment data")
            words_ctm = insert_silences_in_alignment(condensed_words_ctm, split_summary_json, force=force)

            print(f"-- Converting alignment to transcript")
            transcript_json = convert_words_ctm_to_transcript(lyrics_txt, words_ctm, force=force)

            print(f"-- Converting transcript to segments ass")
            subtitles_segments_ass = convert_transcript_to_segments_ass(transcript_json, force=force)

            print(f"-- Converting transcript to words ass")
            subtitles_words_ass = add_words_to_segments_ass(subtitles_segments_ass, transcript_json, force=force)

            print(f"-- Applying karaoke mode to words ass")
            subtitles_karaoke_ass = apply_karaoke_mode_to_words_ass(subtitles_words_ass, force=force)

            print(f"-- Replacing audio track in video")
            video_accompaniment_mp4 = replace_audio_track_in_video(video_mp4, accompaniment_mp3, force=force)

            # print(f"-- Inserting subtitles in video")
            # video_karaoke_mp4 = insert_subtitles_in_video(video_accompaniment_mp4, subtitles_karaoke_ass, force=True)

            # print(f"-- Showing quality report {project_name}")
            # evaluate_quality(vocals_wav, transcript_json)

            media_dir = f'{project_dir}/../media'
            if not os.path.exists(media_dir):
                os.makedirs(media_dir)
            shutil.copy(video_accompaniment_mp4, f'{media_dir}/{os.path.basename(project_dir)}.mp4')
            shutil.copy(subtitles_karaoke_ass, f'{media_dir}/{os.path.basename(project_dir)}.ass')

            # print(f"-- Splitting {speech_to_text_target} track based on vocals silences")
            # target_filename = None if speech_to_text_target == 'vocals' else audio_wav
            # voice_segments_json = split_audio(vocals_wav, target_filename=target_filename, silence_threshold=silence_threshold, min_silence_length=min_silence_length, force=force)
            # print(f"-- Running speech to text on {speech_to_text_target} track")
            # transcript_json = transcribe_segments_speech_to_text(voice_segments_json, language=language, model_name=model_name, initial_prompt=default_initial_prompt, force=force)
            # print("-- Aligning transcription on official lyrics")
            # aligned_transcript_json = align_transcript_on_lyrics(transcript_json, lyrics_txt, language, force=force)
            # print("-- Generating subtitles")
            # convert_transcript_to_segments_ass(aligned_transcript_json)
        except:
            print(traceback.format_exc())

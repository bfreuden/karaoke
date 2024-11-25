from convert_wav_to_mp3 import convert_wav_to_mp3
from download_lyrics import download_lyrics
from download_youtube_video import download_youtube_video
from extract_mp3_from_mp4 import extract_mp3_from_mp4
from get_or_create_karaoke_project_data import get_or_create_project_from_attributes
from split_vocals_and_accompaniment import split_vocals_and_accompaniment
from src.convert_mp3_to_wav import convert_mp3_to_wav
from src.align_transcript_on_lyrics import align_transcript_on_lyrics
from src.split_audio import split_audio
from src.transcribe_speech_to_text import transcribe_segments_speech_to_text
from convert_transcript_to_ass import convert_transcript_to_segments_ass
from fix_segment_start_end_timings import fix_segment_start_end_timings

if __name__ == '__main__':

    from sample_projects import sample_projects, get_sample_project_dir
    # project_name = 'dancing_in_the_dark'
    project_name = 'ma_direction'
    # project_name = 'criminal'
    project_attributes = sample_projects[project_name]
    force = False

    # default values
    default_voice_threshold = 0.001
    default_model_name = 'large-v3'
    default_speech_to_text_target = 'audio'
    default_min_silence_length = 0.45
    default_initial_prompt = None

    print("-- Creating project data")
    karaoke_project_data = get_or_create_project_from_attributes(project_attributes, force=force)

    youtube_url = karaoke_project_data['youtube_url']
    genius_url = karaoke_project_data['genius_url']
    slug = karaoke_project_data['slug']
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
    print(f"-- Splitting {speech_to_text_target} track based on vocals silences")
    target_filename = None if speech_to_text_target == 'vocals' else audio_wav
    voice_segments_json = split_audio(vocals_wav, target_filename=target_filename, silence_threshold=silence_threshold, min_silence_length=min_silence_length, force=force)
    print(f"-- Running speech to text on {speech_to_text_target} track")
    transcript_json = transcribe_segments_speech_to_text(voice_segments_json, language=language, model_name=model_name, initial_prompt=default_initial_prompt, force=force)
    print("-- Aligning transcription on official lyrics")
    aligned_transcript_json = align_transcript_on_lyrics(transcript_json, lyrics_txt, language, force=force)
    print("-- Generating subtitles")
    convert_transcript_to_segments_ass(aligned_transcript_json)

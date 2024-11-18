from convert_wav_to_mp3 import convert_wav_to_mp3
from download_lyrics import download_lyrics
from download_youtube_video import download_youtube_video
from extract_mp3_from_mp4 import extract_mp3_from_mp4
from get_or_create_karaoke_project_data import get_or_create_project_from_attributes
from split_vocals_and_accompaniment import split_vocals_and_accompaniment
from src.fix_transcript import fix_transcript
from transcript_speech_to_text import transcript_speech_to_text
from convert_transcript_to_ass import convert_transcript_to_segments_ass

if __name__ == '__main__':

    from sample_projects import sample_projects, get_sample_project_dir
    project_name = 'dancing_in_the_dark'
    project_attributes = sample_projects[project_name]
    force = False

    print("-- Creating project data")
    karaoke_project_data = get_or_create_project_from_attributes(project_attributes, force=force)

    youtube_url = karaoke_project_data['youtube_url']
    genius_url = karaoke_project_data['genius_url']
    slug = karaoke_project_data['slug']
    language = karaoke_project_data['language']
    model = karaoke_project_data['model']
    project_dir = get_sample_project_dir(project_name)

    print("-- Downloading YouTube video")
    video_mp4 = download_youtube_video(youtube_url, project_dir, force=force)
    print("-- Downloading lyrics")
    lyrics_txt = download_lyrics(genius_url, project_dir, force=force)
    print("-- Extracting audio from video")
    audio_mp3 = extract_mp3_from_mp4(video_mp4, force=force)
    print("-- Splitting audio track in vocals and accompaniment")
    vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(audio_mp3, force=force)
    print("-- Converting vocals track to mp3")
    vocals_mp3 = convert_wav_to_mp3(vocals_wav, force=force)
    print("-- Converting accompaniment track to mp3")
    accompaniment_mp3 = convert_wav_to_mp3(accompaniment_wav, force=force)
    print("-- Running speech to text on audio track")
    transcript_json = transcript_speech_to_text(vocals_mp3, language=language, model=model, initial_prompt=None, force=force)
    print("-- Aligning transcription on official lyrics")
    fixed_transcript_json = fix_transcript(transcript_json, lyrics_txt, language, force=force)
    print("-- Generating subtitles")
    convert_transcript_to_segments_ass(fixed_transcript_json)

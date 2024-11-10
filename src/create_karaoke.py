
from download_youtube_video import download_youtube_video
from extract_mp3_from_mp4 import extract_mp3_from_mp4
from split_vocals_and_accompaniment import split_vocals_and_accompaniment
from convert_wav_to_mp3 import convert_wav_to_mp3
from transcript_speech_to_text import transcript_speech_to_text

if __name__ == '__main__':
    youtube_url = 'https://www.youtube.com/watch?v=huMElOuIMmk'
    language = 'en'
    force = False

    video_mp4 = download_youtube_video(youtube_url, force=force)
    audio_mp3 = extract_mp3_from_mp4(video_mp4, force=force)
    vocals_wav, accompaniment_wav = split_vocals_and_accompaniment(audio_mp3, force=force)
    vocals_mp3 = convert_wav_to_mp3(vocals_wav)
    accompaniment_mp3 = convert_wav_to_mp3(accompaniment_wav)
    vocal_json = transcript_speech_to_text(vocals_mp3, language, force=force)

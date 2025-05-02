import json
import os
import shutil

from scipy.io import wavfile

from add_words_to_segments_ass import add_words_to_segments_ass
from apply_karaoke_mode_to_words_ass import apply_karaoke_mode_to_words_ass
from convert_transcript_to_ass import convert_transcript_to_segments_ass
from convert_wav_to_mono import convert_wav_to_mono
from align_lyrics_with_audio_docker import align_lyrics_with_audio
from convert_words_ctm_to_transcript import convert_words_ctm_to_transcript


def realign_words_in_corrected_segments(transcript_fixed_json, audio_mono_wav, lyrics_syllables_txt, language, force=False):
    project_dir = os.path.dirname(transcript_fixed_json)
    output_file = f"{project_dir}/transcript-fixed-realigned.json"
    if os.path.exists(output_file) and not force:
        return output_file

    vocals_segment_dir = f"{project_dir}/vocals-segments"
    if not os.path.exists(vocals_segment_dir):
        os.makedirs(vocals_segment_dir)

    with open(transcript_fixed_json, mode='r', encoding='utf-8') as file:
        transcript_fixed = json.load(file)
    segments = transcript_fixed["segments"]

    lyrics_syllables = None
    sample_rate, samples = wavfile.read(audio_mono_wav)
    if lyrics_syllables_txt is not None:
        with open(lyrics_syllables_txt, mode='r') as fp:
            lyrics_syllables = [line.rstrip() for line in fp.readlines() if line.strip() != ""]
        if len(segments) != len(lyrics_syllables):
            raise Exception("not the same number of lines in transcript and syllables file")

    audio_mono_wav_list = []
    lyrics_txt_list = []
    for index, segment in enumerate(segments):
        if lyrics_syllables is not None and segment["text"] != lyrics_syllables[index].replace("/", ""):
            raise Exception("not the same line")
        lyrics_txt = f"{vocals_segment_dir}/vocals-mono-{index:03d}.txt"
        lyrics_txt_list.append(lyrics_txt)
        with open(lyrics_txt, mode="w") as fp:
            text = segment["text"] if lyrics_syllables is None else lyrics_syllables[index].replace("/", " ")
            fp.write(text)
        audio_mono_wav = f"{vocals_segment_dir}/vocals-mono-{index:03d}.wav"
        audio_mono_wav_list.append(audio_mono_wav)
        wavfile.write(
            filename=audio_mono_wav,
            rate=sample_rate,
            data=samples[int(segment["start"]*sample_rate):int(segment["end"]*sample_rate)]
        )

    align_lyrics_with_audio(audio_mono_wav_list, lyrics_txt_list, language, force)
    index = 0
    for lyrics_txt, audio_mono_wav, segment in zip (lyrics_txt_list, audio_mono_wav_list, segments):
        words_ctm = f"{os.path.dirname(lyrics_txt)}/ctm/words/{os.path.basename(audio_mono_wav).replace('.wav', '.ctm')}"
        transcript_json = convert_words_ctm_to_transcript(lyrics_txt, words_ctm, force)
        with open(transcript_json, mode="r") as fp:
            transcript_segment = json.load(fp)
        shutil.move(transcript_json, f'{os.path.dirname(lyrics_txt)}/transcript-{index:03d}.json')
        index += 1
        segment["words"].clear()
        for word in transcript_segment["segments"][0]["words"]:
            word["start"] += segment["start"]
            word["end"] += segment["start"]
            segment["words"].append(word)
        segment["words"][0]["start"] = segment["start"]
        segment["words"][-1]["end"] = segment["end"]
    with open(output_file, mode="w") as fp:
        json.dump(transcript_fixed, fp, indent=4)
    return output_file

if __name__ == '__main__':
    from sample_projects import get_sample_project_dir, get_or_create_sample_project
    project_name = 'metallica-turn-the-page'
    project_dir = get_sample_project_dir(project_name)
    project_data  = get_or_create_sample_project(project_name)
    language = project_data['language']

    convert_wav_to_mono(f'{project_dir}/vocals.wav', force=True)

    transcript_json = realign_words_in_corrected_segments(
        f'{project_dir}/transcript-fixed.json',
        f'{project_dir}/vocals-mono.wav',
        None, #f'{project_dir}/lyrics-syllables.txt',
        language,
        force=True
    )

    subtitles_segments_ass = convert_transcript_to_segments_ass(transcript_json, force=True)

    subtitles_words_ass = add_words_to_segments_ass(subtitles_segments_ass, transcript_json, force=True)

    subtitles_karaoke_ass = apply_karaoke_mode_to_words_ass(subtitles_words_ass, force=True)

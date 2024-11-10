# from openai import OpenAI
#
# def transcript_speech_to_text(vocals_mp3):
#   client = OpenAI()
#   with open(vocals_mp3, "rb") as audio_file:
#     transcription = client.audio.transcriptions.create(
#       model="whisper-1",
#       file=audio_file,
#       response_format="verbose_json"
#     )
#     print(transcription.text)

import whisper_timestamped as whisper
import json
import os

def transcript_speech_to_text(vocals_mp3, language, force=False):
    project_dir = os.path.dirname(vocals_mp3)
    output_file = f"{project_dir}/vocals.json"
    if os.path.exists(output_file):
        if force:
            os.remove(output_file)
        else:
            return output_file
    audio = whisper.load_audio(vocals_mp3)
    model = whisper.load_model("medium", device="cpu")
    result = whisper.transcribe(model, audio, language=language)
    with open(output_file, "w") as output:
        json.dump(result, output, indent = 2, ensure_ascii = False)


if __name__ == '__main__':
    from output_dir import output_dir
    transcript_speech_to_text(f'{output_dir}/dancing-in-the-dark/audio.mp3', "en", True)

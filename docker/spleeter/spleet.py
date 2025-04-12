import os
import argparse

os.environ['MODEL_PATH'] = "/opt/spleeter/pretrained_models"

from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator
from spleeter.audio import Codec


parser = argparse.ArgumentParser(description='Resource downloader')
parser.add_argument('input', help='input file', default="/input/audio.mp3")
parser.add_argument('--destination', help='destination', default="/output")
parser.add_argument('--offset', help='offset', default="0.0")
parser.add_argument('--duration', help='duration', default="600.0")
parser.add_argument('--audio-adapter', help='audio adapter', default="spleeter.audio.ffmpeg.FFMPEGProcessAudioAdapter")
parser.add_argument('--codec', help='codec (one of wav, mp3, ogg, m4a, wma, flac)', default="wav")
parser.add_argument('--bitrate', help='bitrate', default="320k")
parser.add_argument('--filename-format', help='filename format', default="{instrument}.{codec}")

args = vars(parser.parse_args())

audio_adapter: AudioAdapter = AudioAdapter.get(args["audio_adapter"])
separator: Separator = Separator("spleeter:2stems", MWF=False)

separator.separate_to_file(
    args["input"],
    args["destination"],
    audio_adapter=audio_adapter,
    offset=float(args["offset"]),
    duration=float(args["duration"]),
    codec=Codec[args["codec"].upper()],
    bitrate=args["bitrate"],
    filename_format=args["filename_format"],
    synchronous=False,
)
separator.join()

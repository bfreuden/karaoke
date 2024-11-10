import os.path

from audio_extract import extract_audio


def extract_mp3_from_mp4(mp4, filename="audio.mp3", force=False):
    project_dir = os.path.dirname(mp4)
    output_file = f"{project_dir}/{filename}"
    if os.path.exists(output_file):
        if force:
            os.remove(output_file)
        else:
            return output_file
    extract_audio(input_path=mp4, output_path=output_file)
    return output_file


if __name__ == '__main__':
    from output_dir import output_dir
    extract_mp3_from_mp4(f'{output_dir}/dancing-in-the-dark/video.mp4', force=True)

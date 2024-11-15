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
    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('dancing_in_the_dark')
    extract_mp3_from_mp4(f'{project_dir}/video.mp4', force=True)

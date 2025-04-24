import os.path
from directories import media_dir


def karaoke_base_name(project_data):
    return f"{project_data['artist']} - {project_data['title']}"

def karaoke_video_file(project_data):
    return f"{karaoke_base_name(project_data)} - karaoke.mp4"

def karaoke_subtitles_file(project_data):
    return f"{karaoke_base_name(project_data)} - karaoke.ass"

def lyrics_video_file(project_data):
    return f"{karaoke_base_name(project_data)} - with lyrics.mp4"

def lyrics_subtitles_file(project_data):
    return f"{karaoke_base_name(project_data)} - with lyrics.ass"


def create_media_links(project_data, video_mp4, video_accompaniment_mp4, subtitles_karaoke_ass, force=False):
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    if force:
        for file in [
            f"{media_dir}/{karaoke_video_file(project_data)}",
            f"{media_dir}/{karaoke_subtitles_file(project_data)}",
            f"{media_dir}/{lyrics_video_file(project_data)}",
            f"{media_dir}/{lyrics_subtitles_file(project_data)}",
        ]:
            if os.path.exists(file):
                os.unlink(file)

    link_path = os.path.relpath(project_dir, start=media_dir)
    os.symlink(f"{link_path}/{os.path.basename(video_accompaniment_mp4)}",
               f"{media_dir}/{karaoke_video_file(project_data)}")
    os.symlink(f"{link_path}/{os.path.basename(subtitles_karaoke_ass)}",
               f"{media_dir}/{karaoke_subtitles_file(project_data)}")
    os.symlink(f"{link_path}/{os.path.basename(video_mp4)}",
               f"{media_dir}/{lyrics_video_file(project_data)}")
    os.symlink(f"{link_path}/{os.path.basename(subtitles_karaoke_ass)}",
               f"{media_dir}/{lyrics_subtitles_file(project_data)}")


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir, get_or_create_sample_project
    project_name = 'metallica-turn-the-page'
    project_dir = get_sample_project_dir(project_name)
    project_data  = get_or_create_sample_project(project_name)
    create_media_links(
        project_data,
        f'{project_dir}/video.mp4',
        f'{project_dir}/video-accompaniment.mp4',
        f'{project_dir}/subtitles-words-karaoke.ass',
        force=True)

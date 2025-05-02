import os.path
from directories import media_dir


def karaoke_base_name(project_data):
    return f"{project_data['artist']} - {project_data['title']}"

def karaoke_video_file_preview(project_data):
    return f"{karaoke_base_name(project_data)} - karaoke (preview).mp4"

def karaoke_subtitles_file_preview(project_data):
    return f"{karaoke_base_name(project_data)} - karaoke (preview).ass"

def lyrics_video_file_preview(project_data):
    return f"{karaoke_base_name(project_data)} - with lyrics (preview).mp4"

def lyrics_subtitles_file_preview(project_data):
    return f"{karaoke_base_name(project_data)} - with lyrics (preview).ass"


def create_media_links_for_generate(project_data, video_mp4, video_accompaniment_mp4, subtitles_karaoke_ass, force=False):
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    project_dir = os.path.dirname(video_mp4)
    link_path = os.path.relpath(project_dir, start=media_dir)
    for src, dest in [
        (f"{link_path}/{os.path.basename(video_accompaniment_mp4)}", f"{media_dir}/{karaoke_video_file_preview(project_data)}"),
        (f"{link_path}/{os.path.basename(subtitles_karaoke_ass)}", f"{media_dir}/{karaoke_subtitles_file_preview(project_data)}"),
        (f"{link_path}/{os.path.basename(video_mp4)}", f"{media_dir}/{lyrics_video_file_preview(project_data)}"),
        (f"{link_path}/{os.path.basename(subtitles_karaoke_ass)}", f"{media_dir}/{lyrics_subtitles_file_preview(project_data)}"),
    ]:
        if os.path.exists(dest) and force:
            os.unlink(dest)
        if not os.path.exists(dest):
            os.symlink(src, dest)


def karaoke_video_file_realigned(project_data):
    return f"{karaoke_base_name(project_data)} - karaoke (realigned).mp4"

def karaoke_subtitles_file_realigned(project_data):
    return f"{karaoke_base_name(project_data)} - karaoke (realigned).ass"

def lyrics_video_file_realigned(project_data):
    return f"{karaoke_base_name(project_data)} - with lyrics (realigned).mp4"

def lyrics_subtitles_file_realigned(project_data):
    return f"{karaoke_base_name(project_data)} - with lyrics (realigned).ass"


def create_media_links_for_realign(project_data, video_mp4, video_accompaniment_mp4, subtitles_karaoke_ass, force=False):
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    project_dir = os.path.dirname(video_mp4)
    link_path = os.path.relpath(project_dir, start=media_dir)
    for src, dest in [
        (f"{link_path}/{os.path.basename(video_accompaniment_mp4)}", f"{media_dir}/{karaoke_video_file_realigned(project_data)}"),
        (f"{link_path}/{os.path.basename(subtitles_karaoke_ass)}", f"{media_dir}/{karaoke_subtitles_file_realigned(project_data)}"),
        (f"{link_path}/{os.path.basename(video_mp4)}", f"{media_dir}/{lyrics_video_file_realigned(project_data)}"),
        (f"{link_path}/{os.path.basename(subtitles_karaoke_ass)}", f"{media_dir}/{lyrics_subtitles_file_realigned(project_data)}"),
    ]:
        if os.path.exists(dest) and force:
            os.unlink(dest)
        if not os.path.exists(dest):
            os.symlink(src, dest)


if __name__ == '__main__':
    from sample_projects import get_sample_project_dir, get_or_create_sample_project
    project_name = 'metallica-turn-the-page'
    project_dir = get_sample_project_dir(project_name)
    project_data  = get_or_create_sample_project(project_name)
    force = False
    create_media_links_for_generate(
        project_data,
        f'{project_dir}/video.mp4',
        f'{project_dir}/video-accompaniment.mp4',
        f'{project_dir}/subtitles-words-karaoke.ass',
        force=force)
    create_media_links_for_realign(
        project_data,
        f'{project_dir}/video.mp4',
        f'{project_dir}/video-accompaniment.mp4',
        f'{project_dir}/subtitles-words-karaoke-fixed.ass',
        force=force)

import os.path
from pathlib import Path


def insert_subtitles_in_video(video_mp4, subtitles_ass, force=False):
    project_dir = os.path.abspath(os.path.dirname(video_mp4))
    video_subtitles_mp4 = os.path.abspath(f"{project_dir}/{Path(os.path.basename(video_mp4)).stem}-karaoke.mp4")
    if os.path.exists(video_subtitles_mp4):
        if force:
            os.remove(video_subtitles_mp4)
        else:
            return video_subtitles_mp4
    # seems to work with mp4 downloaded from youtube but not with with additional track (not re-encoded)?
    # os.system(f'ffmpeg -i {video_mp4} -vf ass={subtitles_ass} {video_subtitles_mp4}')
    # seems to work with mp4 with additional track but not re-encoded
    os.system(f'ffmpeg -i {video_mp4} -filter_complex ass={subtitles_ass}  -c:a copy -c:v libx264 -crf 23 -preset fast  {video_subtitles_mp4}')
    # example of a black video
    # ffmpeg -f lavfi -i color=c=black:s=1920x1080:r=5  -filter_complex ass=subtitles-words-karaoke-fixed.ass  -i accompaniment.mp3 -crf 0 -c:a copy   -c:v libx264 -crf 23 -preset fast -shortest video-black.mp4
    return video_subtitles_mp4

if __name__ == '__main__':
    from sample_projects import get_sample_project_dir
    project_dir = get_sample_project_dir('poets_standstill')
    insert_subtitles_in_video(f'{project_dir}/video-accompaniment.mp4', f'{project_dir}/subtitles-words-karaoke.ass', force=True)

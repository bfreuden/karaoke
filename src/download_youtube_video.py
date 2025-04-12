import os.path

import yt_dlp

def download_youtube_video(youtube_url, output_dir, force=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = f'{output_dir}/video.mp4'
    if os.path.exists(output_file) and not force:
        return output_file
    opts = { 'outtmpl': output_file, 'format': 'best'}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([youtube_url])
    return output_file

if __name__ == '__main__':
    from sample_projects import get_sample_project_items
    project_dir, youtube_url = get_sample_project_items('afi_medicate', 'project_dir', 'youtube_url')
    download_youtube_video(youtube_url, project_dir, force=True)

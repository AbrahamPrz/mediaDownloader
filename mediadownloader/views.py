from __future__ import unicode_literals
from django.shortcuts import render
from .tasks import go_to_sleep
from yt_dlp import YoutubeDL # https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp
import pexpect
import os
import re
import subprocess

NUMBERS_PATTERN = re.compile('[^0-9]|_')

global_task = None

def my_hook(d):    
    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        print("Done downloading {}".format(file_tuple[1])) # print()
    if d['status'] == 'downloading':
        download_progress = str(d['_percent_str']).replace('%', '').strip()
        download_progress = re.sub(NUMBERS_PATTERN, '', download_progress)[3:]
        download_progress = float(download_progress) / 100
        # global_task = go_to_sleep.delay(download_progress, 100)
        print(f'progress: {download_progress}')
    return None # global_task

# Source: https://regex101.com/r/vHEc61/1
YOUTUBE_REGEX = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
# Source: https://regex101.com/r/sC6oR2/174
FACEBOOK_REGEX = r'^https?:\/\/www\.facebook\.com.*\/(video(s)?|watch|story)(\.php?|\/).+$'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MP4_YTDLP_OPTIONS = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 
    'outtmpl': 'video/%(title)s', 
    'progress_hooks': [my_hook],
    'quiet': True,
    # '-loglevel': 'panic',
    'progress': True,
}
MP3_YTDLP_OPTIONS = {
    'format': 'mp3/bestaudio/best',
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }]
}


def index(request):
    context = {}
    if request.method == 'GET':
        print('enviando formulario')
        context['msg'] = 'test'
        context['task'] = None

    else: # POST
        # get url from the html form
        url = str(request.POST['link']).strip()

        # validate url
        if urlValidation(url=url):
            print('recibiendo formulario')
            if 'mp4' in request.POST:
                    # task = go_to_sleep.delay(progress=, total=)
                    # context['global_task'] = global_task.task_id
                    context['task'] = None
                    context['msg'] = 'post'
                    print('MP4 FORMAT')
                    print(BASE_DIR)
                    downloader(url=url, format='mp4')
            else:
                if 'mp3' in request.POST:
                    print('MP3 FORMAT')
                    print(BASE_DIR)
                    downloader(url=url, format='mp3')
                else:
                    print("NOTHING")
        else:
            print("ERROR WITH URL")
    
    return render(request, 'index.html', context)
                

def downloader(url, format):
    ydl_opts = MP4_YTDLP_OPTIONS if format == 'mp4' else MP3_YTDLP_OPTIONS
    # download the video
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        mediainfo = ydl.extract_info(url=url, download=False)
        filename = str(ydl.prepare_filename(mediainfo))
    if format == 'mp4':
        pexpect.run("{BASH_COMMAND} {FILE} {SIZE_LIMIT} \'{FFMPEG_ARGS}\'".format(
            BASH_COMMAND='sh split-video.sh',
            FILE=filename, 
            SIZE_LIMIT='25000000', 
            FFMPEG_ARGS='-c:v libx264 -crf 23 -c:a copy -vf scale=960:-1'))


def urlValidation(url):
        '''
        True = either yt of fb url works
        False = none of those urls are valid
        None = nothing in entry field
        '''
        if len(url) != 0:
            if re.match(YOUTUBE_REGEX, url) or re.match(FACEBOOK_REGEX, url):
                return True
            else:
                return False
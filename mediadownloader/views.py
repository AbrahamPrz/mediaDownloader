from __future__ import unicode_literals
from django.shortcuts import render
import pexpect
import os
import re
from yt_dlp import YoutubeDL
import subprocess

# Source: https://regex101.com/r/vHEc61/1
YOUTUBE_REGEX = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
# Source: https://regex101.com/r/sC6oR2/174
FACEBOOK_REGEX = r'^https?:\/\/www\.facebook\.com.*\/(video(s)?|watch|story)(\.php?|\/).+$'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(request):
    if request.method == 'GET':
        print('enviando formulario')
        return render(request, 'index.html', {
            'msg': 'test',
        })
        
    else: # POST
        # get url from the html form
        url = str(request.POST['link']).strip()

        # validate url
        if urlValidation(url=url):
            print('recibiendo formulario')
            if 'mp4' in request.POST:
                    print('MP4 FORMAT')
                    print(BASE_DIR)
                    mp4download(url=url)
            else:
                if 'mp3' in request.POST:
                    print('MP3 FORMAT')
                    print(BASE_DIR)
                else:
                    print("NOTHING")
        else:
            print("ERROR WITH URL")
    return render(request, 'index.html')
        
# mac de escuela - todas las paginas doubhle sided - tag mac = 35780
# instalar impresora personal a color 310

def my_hook(d):
    if d['status'] == 'finished':
        file_tuple = os.path.split(os.path.abspath(d['filename']))
        print("Done downloading {}".format(file_tuple[1])) # print()
    if d['status'] == 'downloading':
        download_progress = str(d['_percent_str'])
        print(download_progress)
        

def mp4download(url):
    # required to always get mp4 format for videos
    ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 
                'progress_hooks': [my_hook],
                'quiet': True,
                'progress': True,
                'outtmpl': 'videos/%(id)s.%(ext)s'}
        
    # download the video
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url]) # print()
    
        videoinfo = ydl.extract_info(url=url, download=False)
        filename = str(ydl.prepare_filename(videoinfo))
    
    print(pexpect.run("{BASH_COMMAND} {FILE} {SIZE_LIMIT} \'{FFMPEG_ARGS}\'".format(
        BASH_COMMAND='sh split-video.sh',
        FILE=filename, 
        SIZE_LIMIT='25000000', 
        FFMPEG_ARGS='-c:v libx264 -crf 23 -c:a copy -vf scale=960:-1')))


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
from __future__ import unicode_literals
import youtube_dl

def my_hook(d):
    if d["status"] == "finished":
        print "Done downloading, now converting..."


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }],
    'progress_hooks': [my_hook],
    }

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['http://www.youtube.com/watch?v=BaW_jenozKc'])

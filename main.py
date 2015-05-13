from __future__ import unicode_literals
import os, sys

import youtube_dl

from feedgen.feed import FeedGenerator

def run_yt_test(url):

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
        'outtmpl': 'Downloads/%(uploader)s - %(title)s - %(id)s.%(ext)s',
        'writedescription': True,
        'writeinfojson': True,
        'writethumbnail': True,
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        vid_data = ydl.extract_info(url, download = False)
        for key in vid_data.keys():
            print key

        print vid_data["description"]
        #ydl.download([url])

def get_video_info(url):

    with youtube_dl.YoutubeDL() as ydl:
        vid_data = ydl.extract_info(url, download = False)

    return vid_data

def process_video_info(url):
    vid_data = get_video_info(url)
    videos = []
    try:
        videos = vid_data["entries"]
    except KeyError:
        videos = [vid_data,]

    for vid in videos:
        channel_folder = "{id}".format(id = vid["uploader_id"])
        storage_dir = "{root_storage}/{channel_folder}".format( root_storage = "Downloads",
                                                                channel_folder = channel_folder)
        try:
            os.mkdir(storage_dir)
        except OSError as ose:
            if ose.errno != 17:  # File already exists
                sys.exit("ERROR: {}".format(ose))

        channel_info = {"uploader": vid["uploader"],
                        "uploader_id": vid["uploader_id"],
                       }

        with open("{storage_dir}/{name}.txt".format(storage_dir = storage_dir, name = vid["title"]), "wb") as vid_file:
            vid_file.write("Hello")

        #for i in vid_data:
        #    print i

def run_rss_hosting_test():
    fg = FeedGenerator()
    fg.id('http://lernfunk.de/media/654321')
    fg.title('Some Testfeed')
    fg.author( {'name':'John Doe','email':'john@example.de'} )
    fg.link( href='http://example.com', rel='alternate' )
    fg.logo('http://ex.com/logo.jpg')
    fg.subtitle('This is a cool feed!')
    fg.link( href='http://larskiesow.de/test.atom', rel='self' )
    fg.language('en')
    print fg.rss_str(pretty = True)

if __name__ == "__main__":
    url = 'http://www.youtube.com/watch?v=i2fBIUUWRb8'
    vd = process_video_info(url)

    vd = process_video_info('https://www.youtube.com/watch?v=KigIN8BpXk8&list=PLu9l40IymKw-vvGMrd5U-fcimrVjv-9c6')


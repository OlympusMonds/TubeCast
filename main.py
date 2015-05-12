from __future__ import unicode_literals
import youtube_dl

from feedgen.feed import FeedGenerator

def run_yt_test():

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
    run_rss_hosting_test()

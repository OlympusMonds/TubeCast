import youtube_dl
from youtube_dl import DownloadError


def get_video_info(url):
    """
    Uses the YoutubeDL library to download only video info (not the vid itself).
    Accepts vids or playlists. Videos return a different dict to playlists, so 
    it's normalised a bit here
    """
    try:
        with youtube_dl.YoutubeDL() as ydl:
            vid_data = ydl.extract_info(url, download = False)
    except DownloadError as dle:
        print ("ERROR: Unable to download info for {url}. It will be skipped. "
               "Here is some more info:\n{dle}".format(url = url, dle = dle))
        return []

    try:
        videos = vid_data["entries"]  
        # This assumes that "entries" is a surefire to way to know if we have a playlist or not.
        # Could also use "=PL" in url?
    except KeyError:
        videos = [vid_data,]

    return videos


def download_audio(url, output_folder):
    """
    Uses the YouTubeDL library to actually download the vid and convert
    to mp3. Output naming format is defined here, and cache name.
    """

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
        'outtmpl': '{output_folder}/%(id)s - %(title)s.%(ext)s'.format(output_folder=output_folder),
        'writeinfojson': True,
        'writethumbnail': True,
        'download_archive': '{output_folder}/downloaded_videos.txt'.format(output_folder = output_folder)
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except DownloadError as dle:
            print "ERROR - Unable to download mp3 - skipping.\n{dle}".format(dle = dle)



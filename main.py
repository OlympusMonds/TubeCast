from __future__ import unicode_literals
import os, sys
from glob import glob
import json
import pkg_resources

"""
Check for import issues
"""
try:
    pkg_resources.get_distribution("youtube_dl")
    pkg_resources.get_distribution("feedgen")
except pkg_resources.DistributionNotFound as dnfe:
    sys.exit("ERROR - You need the python package '{package}' to use TubeCast.".format(package = dnfe))

import youtube_dl
from youtube_dl import DownloadError
from feedgen.feed import FeedGenerator


from tubecast_host import run_webhost_for_feeds


def make_folder_if_not_there(path):
    """
    Attempts to make a folder if one is not already there
    """
    try:
        os.mkdir(path)
    except OSError as ose:
        if ose.errno != 17:  # File already exists
            sys.exit("ERROR: {}".format(ose))


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
        ydl.download([url])


def get_audio_into_storage(url, root_storage = "Downloads"):
    """
    The main function to get audo from YT. Takes a YT URL (that YoutubeDL would accept), and
    a download location. This function then gets the info about the vid, makes an appropriate
    folder, and then downloads the relevant stuff into the download folder.
    """
    videos = get_video_info(url)

    if len(videos) < 1:
        return
    
    # Initialise storage
    make_folder_if_not_there(root_storage)
    channel_folder = "{id}".format(id = videos[0]["uploader_id"])
    storage_dir = "{root_storage}/{channel_folder}".format(root_storage = "Downloads", 
                                                           channel_folder = channel_folder)
    make_folder_if_not_there(storage_dir)

    for vid in videos:
        try:
            download_audio("https://www.youtube.com/watch?v={}".format(vid["id"]), storage_dir) 
        except DownloadError as dle:  # TODO: get the right exception class
            print "ERROR downloading mp3 - skipping.\n{dle}".format(dle = dle)
        """
        TODO:
        Think if download_audio should be 1 level less indented. If so, ytdl would handle the seperate
        video downloads automatically - but what if it's a custom playlist, with multiple channels?
        Then all vids would be put into the same folder. If it IS indented, it will put each vid into 
        it's own channel folder. Is that what you want..? Should this be an option?
        """


def generate_rss(root_storage):
    """
    Check the root storage folder for channels, and make RSS feeds for all of them
    """
    channels = sorted(glob("{root_storage}/*".format(root_storage = root_storage)))

    feeds = [generate_channel_rss(channel) for channel in channels if os.path.isdir(channel)]
    return feeds


def generate_channel_rss(storage_dir):
    """
    Generate an RSS feed based off the mp3s found in the storage_dir. We also expect to find
    a .json file accompanying each mp3, which has all the details about the file.
    """

    # TODO: Check if pickled object is already around

    channel = os.path.basename(storage_dir)
    extension_to_find = ".mp3"
    mp3_files = glob("{storage_dir}/*{extension_to_find}".format(storage_dir = storage_dir,
                                                                 extension_to_find = extension_to_find))

    if len(mp3_files) < 1:
        print "Skipping channel {channel} - no mp3s found.".format(channel = channel)
        return ""
    else:
        fg = FeedGenerator()
        fg.load_extension("podcast")

        fg.id("http://localhost/tubecast/{channel}".format(channel = channel))
        fg.title("{channel} - TubeCast".format(channel = channel))
        fg.author( {"name" : channel, "email": "n@a.com"} )
        fg.logo("http://localhost/tubecast/{channel}/pic.jpg")
        fg.subtitle('This is a cool feed!')
        fg.link( href='http://localhost/tubecast/file.rss', rel='self' )
        fg.language('en')
        
        for mp3 in mp3_files:
            filename_without_ext = os.path.splitext(mp3)[0]
            try:
                with open("{filename}.info.json".format(filename = filename_without_ext)) as info:
                    vid_data = json.load(info)
            except Exception as e:
                # TODO: improve this..
                sys.exit("ERROR reading json file:\n{}".format(e))
            
            fe = fg.add_entry()
            fe.id("http://localhost/tubecast/{mp3}".format(mp3 = mp3))
            fe.title(vid_data["fulltitle"])
            fe.description(vid_data["description"])
            fe.enclosure("http://localhost/tubecast/{mp3}".format(mp3 = mp3), 0, "audio/mpeg")

        rss_filename = "{storage_dir}/feed.rss".format(storage_dir = storage_dir)
        try:
            fg.rss_file(rss_filename)
        except IOError as ioe:
            sys.exit("Error writing RSS file:\n{}".format(ioe))
        except UnicodeEncodeError as uee:
            print ("Error writing RSS file - there was a unicode encoding error. Computer says:\n"
                   "{uee}\nHere is what it was trying to do:\n{rss}").format(uee = uee, rss = fg.rss_str(pretty = True))

        # TODO: Also pickle this object? May be able to just add?
        return rss_filename


def read_videos_to_download(filename = "Videos to download.txt"):
    """
    Reads a simple text file with a list of YT urls to videos OR playlists.
    Each line is read in, and added to a list. Lines starting with # are ignored.
    """
    try:
        with open(filename, 'r') as vids_to_dl_file:
            vids_to_dl = [ line for line in vids_to_dl_file if not line.startswith("#")]
    except IOError as ioe:
        sys.exit("ERROR reading {filename} to find videos to download:\n{ioe}".format(filename = filename,
                                                                                      ioe = ioe))
    return vids_to_dl


if __name__ == "__main__":
    # TODO:
    # - Don't forget Windows! the / is diff

    root_storage = "Downloads"

    for vid in read_videos_to_download():
        vd = get_audio_into_storage(vid)

    run_webhost_for_feeds()

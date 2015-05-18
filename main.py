from __future__ import unicode_literals
import os
import sys
import pkg_resources

try:
    pkg_resources.get_distribution("youtube_dl")
    pkg_resources.get_distribution("feedgen")
    pkg_resources.get_distribution("flask")
except pkg_resources.DistributionNotFound as dnfe:
    sys.exit("ERROR - You need the python package '{package}' to use TubeCast.".format(package = dnfe))

from flask import Flask, url_for, redirect

from tubecast_youtube import get_video_info, download_audio
from tubecast_rss import generate_rss
#from tubecast_host import run_webhost_for_feeds


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


def make_folder_if_not_there(path):
    """
    Attempts to make a folder if one is not already there
    """
    try:
        os.mkdir(path)
    except OSError as ose:
        if ose.errno != 17:  # If the error is not "File already exists"
            sys.exit("ERROR: {}".format(ose))


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
        download_audio("https://www.youtube.com/watch?v={}".format(vid["id"]), storage_dir) 
    
    """
    TODO:
    Think if download_audio should be 1 level less indented. If so, ytdl would handle the seperate
    video downloads automatically - but what if it's a custom playlist, with multiple channels?
    Then all vids would be put into the same folder. If it IS indented, it will put each vid into 
    it's own channel folder. Is that what you want..? Should this be an option?
    """


if __name__ == "__main__":
    # TODO:
    # - Don't forget Windows! the / is diff

    root_storage = "Downloads"

    for vid in read_videos_to_download():
        vd = get_audio_into_storage(vid)

   
    feeds = generate_rss(root_storage)    
    
    
    #tubecast_host = Flask(__name__)
    #tubecast_host.debug = debug
    #tubecast_host.run()


import os
import sys
import pkg_resources

try:
    pkg_resources.get_distribution("youtube_dl")
    pkg_resources.get_distribution("feedgen")
    pkg_resources.get_distribution("flask")
except pkg_resources.DistributionNotFound as dnfe:
    sys.exit("ERROR - You need the python package '{package}' to use TubeCast.".format(package = dnfe))

from tubecast_youtube import get_video_info, download_audio
from tubecast_rss import generate_rss
from tubecast_host import start_rss_host


def read_videos_to_download(filename = "Videos to download.txt"):
    """
    Reads a simple text file with a list of YT urls to videos OR playlists.
    Each line is read in, and added to a list. Lines starting with # are ignored.
    """
    try:
        with open(filename, 'r') as vids_to_dl_file:
            vids_to_dl = [ line for line in vids_to_dl_file if not line.startswith("#")]
    except IOError as ioe:
        if ioe.errno == 2:
            sys.exit(("You need to make a file called \"{filename}\" and put a list of YouTube URLs in it, "
                      "one per line.\nIf you put a # at the start of a line, it will be ignored".format(filename=filename)))
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
    storage_dir = os.path.join(root_storage, channel_folder)
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

    root_storage = "Downloads"
    host_ip_address = None
    host_port = 8080

    # Do the Youtube stuff
    #for vid in read_videos_to_download():
    #    vd = get_audio_into_storage(vid, root_storage)

    # Do the RSS stuff
    feeds = generate_rss(root_storage, host_ip_address, host_port)    
    
    # Do the web hosting stuff
    start_rss_host(root_storage, feeds, host_ip_address, host_port)

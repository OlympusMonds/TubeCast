from glob import glob
import os
import sys
import json
from collections import OrderedDict
import socket

from feedgen.feed import FeedGenerator


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        ip = s.getsockname()[0]
        s.close()
    except Exception as e:  # TODO find better exception
        sys.exit(e)
    return ip


def generate_rss(root_storage, host_ip_address = None, host_port = 8080):
    """
    Check the root storage folder for channels, and make RSS feeds for all of them
    """
    ip = get_local_ip() if host_ip_address is None else host_ip_address
    ip = "{ip}:{port}".format(ip=ip, port=host_port)

    channels = [ folder for folder in sorted(glob(os.path.join(root_storage, "*"))) if os.path.isdir(folder) ]
    
    all_media = []
    feeds = []
    for channel in channels:
        media = find_media_to_add_to_rss(channel)
        all_media.extend(media)
        feeds.append(generate_rss_feed_from_media(media, ip, root_storage, channel = channel))

    # Now make a global rss feed
    feeds.append(generate_rss_feed_from_media(all_media, ip, root_storage))
    channels.append("AllMedia")

    nice_feeds = OrderedDict()
    for pretty_channel, feed_url in zip(channels, feeds):
        nice_feeds[os.path.basename(pretty_channel)] = feed_url

    return nice_feeds


def find_media_to_add_to_rss(storage_dir):
    """
    Find all the relevant media recursively from this storage_dir.
    This could be applied to the Downloads folder, and work equally well
    """
    media_to_rss = []
    for root, subfolders, files in os.walk(storage_dir):
        interesting_files = [ f for f in files if f.endswith(("mp3", "mp4")) ]
        for f in interesting_files:
            media_to_rss.append(os.path.join(root, f))

    return media_to_rss


def generate_rss_feed_from_media(media_to_rss, ip, root_dir, channel = None):
    if len(media_to_rss) < 1:
        return None

    global_channel = False 
    if channel is None:
        channel = "AllMedia"
        global_channel = True


    fg = FeedGenerator()
    fg.load_extension("podcast")

    fg.id("http://{ip}/feed/{channel}".format(ip = ip, channel = channel))
    fg.title("{channel} - TubeCast".format(channel = channel))
    fg.author( {"name" : channel, "email": "n@a.com"} )
    fg.logo("http://{ip}/feed/{channel}/pic.jpg".format(ip = ip, channel = channel))
    fg.subtitle('This is a cool feed!')
    fg.link( href='http://{ip}/feed/{channel}/feed.rss'.format(ip = ip, channel = channel), rel='self' )
    fg.language('en')

    for media_file in media_to_rss:
        media_file_basename = os.path.basename(media_file)
        channel_dir = os.path.split(os.path.dirname(media_file))[1]  # Oh god, the worst!
        filepath_without_ext = os.path.splitext(media_file)[0]
        filename_without_ext = os.path.splitext(media_file_basename)[0]
        url_safe_filename = media_file_basename.replace(" ", "%20")

        jpeg_filename = "{}.jpg".format(filename_without_ext)
        json_filename = "{}.info.json".format(filepath_without_ext)

        try:
            with open(json_filename) as info:
                vid_data = json.load(info)
        except Exception as e:
            # TODO: find real exception
            sys.exit("ERROR reading json file:\n{}".format(e))

        if global_channel:
            channel = channel_dir

        fe = fg.add_entry()
        fe.id("http://{ip}/feed/{channel}/{mp}".format(ip = ip, channel = channel, mp = url_safe_filename))
        fe.title(vid_data["fulltitle"])
        fe.description(vid_data["description"])
        if media_file.endswith("mp3"):
            fe.enclosure("http://{ip}/feed/{channel}/{mp}".format(ip = ip, channel = channel, mp = url_safe_filename), 0, "audio/mpeg")
        elif media_file.endswith("mp4"):
            fe.enclosure("http://{ip}/feed/{channel}/{mp}".format(ip = ip, channel = channel, mp = url_safe_filename), 0, "video/mp4")
        fe.podcast.itunes_image("http://{ip}/feed/{channel}/{base_jpg_filename}".format(ip = ip, channel = channel, base_jpg_filename = jpeg_filename))

    if global_channel:
        rss_filename = os.path.join(root_dir, "feed.rss")
    else:
        rss_filename = os.path.join(channel, "feed.rss")

    try:
        fg.rss_file(rss_filename)
    except IOError as ioe:
        sys.exit("Error writing RSS file:\n{}".format(ioe))
    except UnicodeEncodeError as uee:
        print ("Error writing RSS file - there was a unicode encoding error. Computer says:\n"
               "{uee}\nHere is what it was trying to do:\n{rss}").format(uee = uee, rss = fg.rss_str(pretty = True))

    return rss_filename


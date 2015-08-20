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

    channels = sorted(glob(os.path.join(root_storage, "*")))
    feeds = [generate_channel_rss(channel, ip) for channel in channels if os.path.isdir(channel)]

    nice_feeds = OrderedDict()
    for pretty_channel, feed_url in zip(channels, feeds):
        nice_feeds[os.path.basename(pretty_channel)] = feed_url

    return nice_feeds


def generate_channel_rss(storage_dir, ip):
    """
    Generate an RSS feed based off the mp3s found in the storage_dir. We also expect to find
    a .json file accompanying each mp3, which has all the details about the file.
    """

    # TODO: Check if pickled object is already around

    channel = os.path.basename(storage_dir)
    extension_to_find = ".mp*"
    mp_files = glob(os.path.join(storage_dir, "*{}".format(extension_to_find)))

    if len(mp_files) < 1:
        print "Skipping channel {channel} - no mp3s found.".format(channel = channel)
        return ""
    else:
        fg = FeedGenerator()
        fg.load_extension("podcast")

        fg.id("http://{ip}/feed/{channel}".format(ip = ip, channel = channel))
        fg.title("{channel} - TubeCast".format(channel = channel))
        fg.author( {"name" : channel, "email": "n@a.com"} )
        fg.logo("http://{ip}/feed/{channel}/pic.jpg".format(ip = ip, channel = channel))
        fg.subtitle('This is a cool feed!')
        fg.link( href='http://{ip}/feed/{channel}/feed.rss'.format(ip = ip, channel = channel), rel='self' )
        fg.language('en')

        have_mp3, have_mp4 = False, False
        for mp in mp_files:
            filename_without_ext = os.path.splitext(mp)[0]
            base_mp_filename = os.path.basename(mp).replace(" ", "%20")
            if mp.endswith("mp3"):
                have_mp3 = True
                base_jpg_filename = os.path.basename(mp.replace(".mp3", ".jpg"))
            elif mp.endswith("mp4"):
                have_mp4 = True
                base_jpg_filename = os.path.basename(mp.replace(".mp4", ".jpg"))

            try:
                with open("{filename}.info.json".format(filename = filename_without_ext)) as info:
                    vid_data = json.load(info)
            except Exception as e:
                # TODO: find real exception
                sys.exit("ERROR reading json file:\n{}".format(e))

            fe = fg.add_entry()
            fe.id("http://{ip}/feed/{channel}/{mp}".format(ip = ip, channel = channel, mp = base_mp_filename))
            fe.title(vid_data["fulltitle"])
            fe.description(vid_data["description"])
            if have_mp3:
                fe.enclosure("http://{ip}/feed/{channel}/{mp}".format(ip = ip, channel = channel, mp = base_mp_filename), 0, "audio/mpeg")
            elif have_mp4:
                fe.enclosure("http://{ip}/feed/{channel}/{mp}".format(ip = ip, channel = channel, mp = base_mp_filename), 0, "video/mp4")
            fe.podcast.itunes_image("http://{ip}/feed/{channel}/{base_jpg_filename}".format(ip = ip, channel = channel, base_jpg_filename = base_jpg_filename))

        rss_filename = os.path.join(storage_dir, "feed.rss")
        try:
            fg.rss_file(rss_filename)
        except IOError as ioe:
            sys.exit("Error writing RSS file:\n{}".format(ioe))
        except UnicodeEncodeError as uee:
            print ("Error writing RSS file - there was a unicode encoding error. Computer says:\n"
                   "{uee}\nHere is what it was trying to do:\n{rss}").format(uee = uee, rss = fg.rss_str(pretty = True))

        # TODO: Also pickle this object? May be able to just add?
        return rss_filename

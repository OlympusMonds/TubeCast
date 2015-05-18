from glob import glob
import os
import sys
import json
from feedgen.feed import FeedGenerator


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


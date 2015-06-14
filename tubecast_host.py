from glob import glob
import os
from collections import OrderedDict

from flask import Flask, url_for, redirect, send_from_directory


# TODO: This seems like an enormous hack...
tch_flask = Flask(__name__)


class TubeCastRSSHost():
    """
    This class is designed to be a persistent in-memory db of all
    rss feeds available. When it starts up, you can pass it a list
    of feeds, but if needed it can update by scanning the file 
    structure.
    """
    
    def __init__(self, root_storage, feed_paths):
        self.feed_paths = feed_paths
        self.root_storage = root_storage

    def update_feed_paths(self):
        self.feed_paths = OrderedDict()
        for channel in sorted(glob(os.path.join(self.root_storage, "*"))):
            if os.path.isdir(channel):
                if os.path.isfile(os.path.join(channel, "feed.rss")):
                    pretty_channel = os.path.basename(channel)
                    self.feed_paths[pretty_channel] = os.path.join(channel, "feed.rss")

    @property
    def feeds(self):
        return self.feed_paths



@tch_flask.route("/feed/<feedname>/<filename>")
def get_file(feedname, filename):
    feed_names = tch_flask.config["TubeCastRSSHost"].feeds
    root_storage = tch_flask.config["root_storage"]
    if feedname in feed_names.keys():
        if filename.endswith(("jpg", "mp3")):
            return send_from_directory(os.path.join(root_storage, feedname), filename)
    return redirect(url_for("show_feeds"))


@tch_flask.route("/feed/<feedname>")
def show_feed(feedname):
    feed_paths = tch_flask.config["TubeCastRSSHost"].feeds
    rss_filename = "feed.rss"
    rss_path = os.path.dirname(feed_paths[feedname])
    return send_from_directory(rss_path, rss_filename, as_attachment = True, attachment_filename=rss_filename)


@tch_flask.route("/feeds/update")
def update_feeds():
    tch_flask.config["TubeCastRSSHost"].update_feed_paths()
    return redirect(url_for("show_feeds"))


@tch_flask.route("/feeds/")
def show_feeds():
    """
    Get a list of channels with feeds (by scanning the folders), and display a simple
    list on a page
    """
    feed_paths = tch_flask.config["TubeCastRSSHost"].feeds
    text = ["Channel feeds available:",]
    for channel, feed_url in feed_paths.iteritems():
        text.append("<a href=\"/feed/{channel}\">  - {channel}  </a>".format(channel = channel))
    text.append("<a href=\"/feeds/update\">Update feeds</a>")
    return "<br \>".join(text)
                  

def start_rss_host(root_storage, feed_paths, host_ip_address, host_port):
    tch_flask.debug = False
    tch_flask.config["TubeCastRSSHost"] = TubeCastRSSHost(root_storage, feed_paths)
    tch_flask.config["root_storage"] = root_storage

    tch_flask.run(host='0.0.0.0', port=host_port)


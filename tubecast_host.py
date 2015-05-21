from glob import glob
import os

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
        self.feed_paths = {}
        for channel in sorted(glob("{root_storage}/*".format(root_storage = self.root_storage))):
            if os.path.isdir(channel):
                if os.path.isfile("{channel}/feed.rss".format(channel = channel)):
                    pretty_channel = os.path.basename(channel)
                    self.feed_paths[pretty_channel] = "{channel}/feed.rss".format(channel = channel)


    @property
    def feeds(self):
        return self.feed_paths



@tch_flask.route("/feed/<feedname>")
def show_feed(feedname):
    feed_paths = tch_flask.config["TubeCastRSSHost"].feeds
    rss_filename = "feed.rss"
    rss_path = os.path.dirname(feed_paths[feedname])
    return send_from_directory(rss_path, rss_filename, as_attachment = True, attachment_filename=rss_filename)

    #return "This is the feed for {}".format(feedname)
    #return "Feed: {feedname}".format(feedname = feedname)


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
        text.append("<a href=\"/feed/{feed_url}\">  - {channel}  </a>".format(feed_url = channel, channel = channel))
    text.append("<a href=\"/feeds/update\">Update feeds</a>")
    return "<br \>".join(text)
                  

def start_rss_host(root_storage, feed_paths):
    tch_flask.debug = True
    tch_flask.config["TubeCastRSSHost"] = TubeCastRSSHost(root_storage, feed_paths)

    tch_flask.run(host='0.0.0.0')

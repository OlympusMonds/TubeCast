from glob import glob
import os

from flask import Flask, url_for, redirect

class TubeCastRSSHost():

    def __init__(self, root_storage, feed_paths):
        self.feed_paths = feed_paths
        self.root_storage = root_storage

    
    def update_feed_paths():
        self.feed_paths = []
        for channel in sorted(glob("{root_storage}/*".format(root_storage = self.root_storage))):
            if os.path.isdir(channel):
                if os.path.isfile("{channel}/feed.rss".format(channel = channel)):
                    self.feed_paths.append("{channel}/feed.rss".format(channel = channel))


    @property
    def feeds():
        return self.feed_paths


@tch_flask.route("/feed/<feedname>")
def show_feed(feedname):
    return "This is the feed for {}".format(feedname)
    #print url_for('static', filename="style.css")
    #return "Feed: {feedname}".format(feedname = feedname)


@tch_flask.route("/feeds/update")
def update_feeds():
    return redirect(url_for("show_feeds"))


@tch_flask.route("/feeds/")
def show_feeds():
    """
    Get a list of channels with feeds (by scanning the folders), and display a simple
    list on a page
    """
    text = ["Channel feeds available:",]
    for channel in feed_paths:
        text.append("<a href=\"/feed/{channel}\">  - {channel}  </a>".format(channel = os.path.basename(channel)))
    text.append("<a href=\"/feeds/update\">Update feeds</a>")
    return "<br \>".join(text)
                  

def start_rss_host(root_storage, feed_paths):
    tch_flask = Flask(__name__)
    tch_flask.debug = True

    tc_rss_host = TubeCastRSSHost(root_storage, feed_paths)

    tch_flask.run()

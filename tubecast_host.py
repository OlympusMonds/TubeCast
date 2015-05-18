from glob import glob
import os

from flask import url_for, redirect
from flask.views import View


class TubeCast_RSS_Host(View):

    feed_paths = []

    @tubecast_host.route("/feed/<feedname>")
    def show_feed(feedname):
        print url_for('static', filename="style.css")
        return "Feed: {feedname}".format(feedname = feedname)

    @tubecast_host.route("/feeds/update")
    def update_feed_paths():
        feed_paths = []
        for channel in sorted(glob("{root_storage}/*".format(root_storage = "Downloads"))):
            if os.path.isdir(channel):
                if os.path.isfile("{channel}/feed.rss".format(channel = channel)):
                    feed_paths.append("{channel}/feed.rss".format(channel = channel))

        return redirect(url_for("show_feeds"))


    @tubecast_host.route("/feeds/")
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
                  


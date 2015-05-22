# TubeCast
Convert a YouTube channel into a local RSS source for a podcast app to pickup.

## Important Note ##
This program no way intends to stop content creators receiving payment via ads (or whatever). While perhaps naive, the intent is to be able to consume their content in a more convienient way for those who either get motion-sickness on public transport, or can't afford the data costs of mobile YouTube.
I would recommend you look to see if the creator you're TubeCasting has a Patreon, or similar, to support them.

# Dependencies
The main dependencies are:
 - YoutubeDL - https://github.com/rg3/youtube-dl
 - FeedGenerator - http://lkiesow.github.io/python-feedgen/
 - Flask - https://github.com/mitsuhiko/flask


# Design Choices
TubeCast has been built in a very modular way, so that the three main sections (Youtube, feed generation, file hosting) are distinctly separate. There are areas where the program could probably be a lot more efficient or clean, but at the cost of this modularity.

For example, the Youtube-dl api does allow one to access the video description in code, which could potentially be passed straight through the the RSS feed generator. Instead, TubeCast asks Youtube-dl to download the video info to JSON, which the RSS generator then loads in and reads to populate it's entry info.
This initially feels perhaps like an odd choice (it did to me), but the de-coupling allows each module to behave independently, and specifically for this example, allows users to remove videos from their download list (to save Youtube-dl from having to check them), while still generating an RSS feed that includes these older episodes.
Another perfect example of the advantage of de-coupling is if the user has their own hosting server that is not Flask. In this case, disabling Flask is very easy. Initial design ideas were for Flask to be the GUI for TubeCast (and potentially it could), but the de-coupled approach won out.


# TODO
 - Add flexibility in functionality. Someone may have their own server to host, etc. Allow users to pick which operations to do.

[![Code Issues](http://www.quantifiedcode.com/api/v1/project/c52e5b9ea3c84088836765c076a196f6/badge.svg)](http://www.quantifiedcode.com/app/project/c52e5b9ea3c84088836765c076a196f6)

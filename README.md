# TubeCast
Convert a YouTube channel into a local RSS source for a podcast app to pickup.

Sometimes you don't have time to sit down and watch a long YouTube video of a movie review or talk. You would like to, but the only time you really have is on the way to work on a bus or train. The problem: you get motion-sickness, so you're limited to podcasting*. Or, you can't afford the data costs, since the YouTube app won't cache videos.

TubeCast allows you to download YouTube videos onto your local computer, and then host them as a podcast RSS feed. You can use any podcast app on your phone (with all its bells-and-whistles) to copy the audio or videos from your computer. So long as your computer and phone are on the same network, there will be no data usage. Then you can consume the media you want when you can!

*"Limited to podcasting" is a misnomer, because podcasts are great!

## Important Note ##
This program no way intends to stop content creators receiving payment via ads (or whatever). While perhaps naive, the intent is to be able to consume their content in a more convienient way for those who either get motion-sickness on public transport, or can't afford the data costs of mobile YouTube.
I would recommend you look to see if the creator you're TubeCasting has a Patreon, or similar, to support them.

**Update:** This program is clearly in violation of the YouTube terms of service, as I assume youtube-dl must be also. Dang.

# Dependencies
The main dependencies are:
 - YoutubeDL - https://github.com/rg3/youtube-dl
 - FeedGenerator - http://lkiesow.github.io/python-feedgen/
 - Flask - https://github.com/mitsuhiko/flask


# Design Choices
TubeCast has been built in a very modular way, so that the three main sections (Youtube, feed generation, file hosting) are distinctly separate. There are areas where the program could probably be a lot more efficient or clean, but at the cost of this modularity.

For example, the Youtube-dl api does allow one to access the video description easily in Python. This data could be passed straight through the the RSS feed generator. Instead, TubeCast asks Youtube-dl to download the video info to JSON, which the RSS generator then loads in and reads to populate it's entry info.

This initially feels perhaps like an odd choice (it did to me), but the de-coupling allows each module to behave independently, and specifically for this example, allows users to remove videos from their download list (to save Youtube-dl from having to check them), while still generating an RSS feed that includes these older episodes.

Another perfect example of the advantage of de-coupling is if the user has their own hosting server that is not Flask. In this case, disabling Flask is very easy, and so using a seperate static file hosting would be easy.


# TODO
 - Add more CLI args (download location, storage location). Perhaps look at saving a config file.
 - Youtube-dl does have a flag for downloading ads too. Experiment with this.
 - Need to be able to abstract away from direct IP, as people's IP addresses change with DHCP. Can I find a DNS or localname to be used on the network?

[![Code Issues](http://www.quantifiedcode.com/api/v1/project/c52e5b9ea3c84088836765c076a196f6/badge.svg)](http://www.quantifiedcode.com/app/project/c52e5b9ea3c84088836765c076a196f6)

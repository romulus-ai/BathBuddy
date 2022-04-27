# Bathbuddy

Bathbuddy is you smart buddy to help you catch the nice time for handwashing and teeth washing. Additionally it makes this time great by supporting you with music.


## Requirements

A registered App at "https://developer.spotify.com/" you will need the clientid and the client secret.
A Spotify Premium Account
A Device registered at spotify to play the music on. Here I suggest using spotifyd.
Maybe a Raspberry Pi and some musicbox

## Make it your Buddy

To make this small script your real buddy, it needs some more as only the script.

Setup a raspi with raspbian.
Install and configure spotifyd (https://github.com/Spotifyd/spotifyd)
Install this script (folder python) in some directory on your server (i.e. /opt/bathbuddy/) and install its requirements (pip install -r requirements.txt)
Install nginx and configure it fore execution of scripts via cgi (see folder nginx)
Install the shell scripts start the music for different situations to /var/www

## The ESP Component (following)

This part need to be created yet.

Plan is, ESP8266-01S, with 3 buttons connected. On Button is a fancy buttong a the soap dispenser. The ESP runs on battery and uses sleep mode as well. Everytime a button is push it sends a http request to the nginx running on the rapi, which then starts the music.

## Todo:

- Install everything except raspbian on py by using ansible.
- Creating the ESP Code and provide a png showing the electric plan (fritzing)
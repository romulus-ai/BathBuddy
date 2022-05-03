# flask_web/app.py

from flask import Flask
import spotipy
import random
import docker
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
from threading import Thread

app = Flask(__name__)
app.config.from_pyfile('/app/settings.cfg')

spotify = ""
device_id = ""
docker_client = ""
scope = "user-read-playback-state,user-modify-playback-state,playlist-read-collaborative,playlist-read-private,streaming"
isplaying = False
devices = ""

@app.route('/handwash')
def handwash():
    # Plays music for 30secs
    if not isplaying:
        thread = Thread(target=playmusic, args=(30,))
        thread.daemon = True
        thread.start()
        return 'Playing music 30sec'
    return 'Music already playing'

@app.route('/infinite')
def infinite():
    if isplaying:
      stopmusic()
      return 'stopping music'
    else:
      playmusic(0)
      return 'Playing music until stopped'

@app.route('/toothbrush')
def toothbrush():
    # Plays music for 2mins
    if not isplaying:
        thread = Thread(target=playmusic, args=(120,))
        thread.daemon = True
        thread.start()
        return 'Playing music 2mins'
    return 'Music already playing'

# Workaround because of an issue in librespot
# https://github.com/Spotifyd/spotifyd/issues/903
# https://github.com/librespot-org/librespot/issues/247
@app.route('/check')
def check():
    return check_bathplayer(app.config["BATHPLAYER_NAME"])

def create_spotify(app_id, app_secret, scope):
  global spotify
  auth_manager = SpotifyOAuth(client_id=app_id, client_secret=app_secret, redirect_uri="http://localhost:8888", scope=scope, open_browser=False)

  spotify = spotipy.Spotify(auth_manager=auth_manager)

  return auth_manager, spotify

# Workaround because of an issue in librespot
# https://github.com/Spotifyd/spotifyd/issues/903
# https://github.com/librespot-org/librespot/issues/247
def create_docker_client():
  global docker_client
  docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  return docker_client

def fetch_bathplayer(bathplayer_name):
  global device_id
  fetch_spotify_devices()
  for device in devices['devices']:
    if device['name'] == bathplayer_name:
      device_id = device['id']

def playmusic(duration):
    global isplaying

    plstr = 'spotify:playlist:' + app.config["PLAYLIST_ID"]
    offset = 0

    playlist_tracks = []

    while True:
      response = spotify.playlist_items(plstr, offset=offset, fields='items.track.id,total', additional_types=['track'])

      if len(response['items']) == 0:
          break

      for track in response['items']:
        id = "spotify:track:" + track['track']['id']
        playlist_tracks.append(id)
      offset = offset + len(response['items'])

    random.shuffle(playlist_tracks)

    print("playing music for " + str(duration) + " seconds")

    spotify.start_playback(device_id=device_id,uris=playlist_tracks)
    isplaying = True

    if duration > 0:
      sleep(duration)
      spotify.pause_playback(device_id=device_id)
      isplaying = False

def stopmusic():
    global isplaying
    spotify.pause_playback(device_id=device_id)
    isplaying = False

# Workaround because of an issue in librespot
# https://github.com/Spotifyd/spotifyd/issues/903
# https://github.com/librespot-org/librespot/issues/247

def check_bathplayer(bathplayer_name):
  global device_id
  global devices
  devices = spotify.devices()
  for device in devices['devices']:
    if device['name'] == bathplayer_name:
      return "Spotifyd is running!"
  return restart_spotifyd()

def restart_spotifyd():
  for container in docker_client.containers.list():
    if "spotifyd" in container.attrs['Config']['Image']:
      if "spotifyd" in container.attrs['Config']['Name']:
        container.restart()
        return "Spotifyd restarted"
  return "Spotifyd not restarted"

def fetch_spotify_devices():
  global devices
  devices = spotify.devices()

if __name__ == '__main__':
    create_spotify(app.config["APP_ID"] , app.config["APP_SECRET"], scope)
    create_docker_client()
    fetch_spotify_devices()

    fetch_bathplayer(app.config["BATHPLAYER_NAME"])

    app.run(debug=True, host='0.0.0.0')
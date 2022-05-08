# flask_web/app.py

from flask import Flask
from flask import render_template
from flask import request
import spotipy
import random
import docker
import time
import re
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

@app.route('/', methods=['POST', 'GET'])
@app.route('/config', methods=['POST', 'GET'])
def config():
    if request.method == 'POST':
      app.config['PLAYLIST_ID'] = request.form.get('playlist')
      app.config['PLAYLIST_ID_1'] = request.form.get('playlist1')
      app.config['PLAYLIST_ID_2'] = request.form.get('playlist2')
      app.config['PLAYLIST_ID_3'] = request.form.get('playlist3')
      app.config['TIMERANGE_1'] = verify_timerange(request.form.get('timerange1'))
      app.config['TIMERANGE_2'] = verify_timerange(request.form.get('timerange2'))
      app.config['TIMERANGE_3'] = verify_timerange(request.form.get('timerange3'))
      app.config['NO_PLAY_TIME'] = verify_timerange(request.form.get('no_play_time'))

      conffile = open("/app/settings.cfg","w+")
      conffile.write("APP_ID = \"%s\"\n" % app.config['APP_ID'])
      conffile.write("APP_SECRET = \"%s\"\n" % app.config['APP_SECRET'])
      conffile.write("PLAYLIST_ID = \"%s\"\n" % app.config['PLAYLIST_ID'])
      conffile.write("PLAYLIST_ID_1 = \"%s\"\n" % app.config['PLAYLIST_ID_1'])
      conffile.write("PLAYLIST_ID_2 = \"%s\"\n" % app.config['PLAYLIST_ID_2'])
      conffile.write("PLAYLIST_ID_3 = \"%s\"\n" % app.config['PLAYLIST_ID_3'])
      conffile.write("TIMERANGE_1 = \"%s\"\n" % app.config['TIMERANGE_1'])
      conffile.write("TIMERANGE_2 = \"%s\"\n" % app.config['TIMERANGE_2'])
      conffile.write("TIMERANGE_3 = \"%s\"\n" % app.config['TIMERANGE_3'])
      conffile.write("NO_PLAY_TIME = \"%s\"\n" % app.config['NO_PLAY_TIME'])
      conffile.write("BATHPLAYER_NAME = \"%s\"\n" % app.config['BATHPLAYER_NAME'])
      conffile.close()

    playlist_names = {}
    playlist_names[app.config['PLAYLIST_ID']] = verify_playlist(app.config['PLAYLIST_ID'])
    playlist_names[app.config['PLAYLIST_ID_1']] = verify_playlist(app.config['PLAYLIST_ID_1'])
    playlist_names[app.config['PLAYLIST_ID_2']] = verify_playlist(app.config['PLAYLIST_ID_2'])
    playlist_names[app.config['PLAYLIST_ID_3']] = verify_playlist(app.config['PLAYLIST_ID_3'])

    return render_template('config-input.html', config = app.config, playlist_names = playlist_names)

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

    fetch_bathplayer(app.config["BATHPLAYER_NAME"])

    if withinTimerange(app.config("NO_PLAY_TIME")):
      return

    plstr = 'spotify:playlist:' + app.config["PLAYLIST_ID"]
    if withinTimerange(app.config("TIMERANGE1")):
      if app.config["PLAYLIST_ID_1"] != "--":
        plstr = 'spotify:playlist:' + app.config["PLAYLIST_ID_1"]
    if withinTimerange(app.config("TIMERANGE2")):
      if app.config["PLAYLIST_ID_2"] != "--":
        plstr = 'spotify:playlist:' + app.config["PLAYLIST_ID_2"]
    if withinTimerange(app.config("TIMERANGE3")):
      if app.config["PLAYLIST_ID_3"] != "--":
        plstr = 'spotify:playlist:' + app.config["PLAYLIST_ID_3"]

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
      return "Spotifyd session is ok!"
  return restart_spotifyd()

def restart_spotifyd():
  for container in docker_client.containers.list():
    if "spotifyd" in container.attrs['Config']['Image']:
      container.restart()
      return "Spotifyd restarted"
  return "Spotifyd not restarted"

def fetch_spotify_devices():
  global devices
  devices = spotify.devices()

def verify_timerange(timerange):
  pattern = re.compile("^((2[0-3]|[01]?[0-9])-(2[0-3]|[01]?[0-9]))|--$")
  if pattern.match(timerange):
    tr = timerange.split("-")
    return timerange
  if not timerange:
    return "--"
  raise Exception("Timerange not valid: %s\n" % timerange)

def verify_playlist(playlist_id):
  if not playlist_id:
    return "--"
  playlistname = spotify.playlist(playlist_id)['name']
  return playlistname

def withinTimerange(range):
  if range == "--":
    return False
  timerange = range.split("-")

  current_time = time.localtime()
  today = time.strftime("%d %m %Y", current_time)

  if timerange[0] <= timerange[1]:
    range_begin = time.strptime(today + " " + timerange[0], "%d %m %Y %H")
    range_end = time.strptime(today + " " + timerange[0], "%d %m %Y %H")
  if timerange[0] > timerange[1]:
    yesterday = time.localtime(time.time()-86400)
    range_begin = time.strptime(yesterday + " " + timerange[0], "%d %m %Y %H")
    range_end = time.strptime(today + " " + timerange[0], "%d %m %Y %H")

  if current_time >= range_begin and current_time <= range_end:
    return True
  return False



if __name__ == '__main__':
    create_spotify(app.config["APP_ID"] , app.config["APP_SECRET"], scope)
    create_docker_client()
    fetch_spotify_devices()

    fetch_bathplayer(app.config["BATHPLAYER_NAME"])

    app.run(debug=True, host='0.0.0.0')
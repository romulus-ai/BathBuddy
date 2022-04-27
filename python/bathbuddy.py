import spotipy
import random
import configparser, argparse, os
from spotipy.oauth2 import SpotifyOAuth
from time import sleep


args = ""
app_id = ""
app_secret = ""
user_id = ""
playlist_id = ""
bathplayer_name = ""
playing_duration = 30
scope = "user-read-playback-state,user-modify-playback-state,playlist-read-collaborative,playlist-read-private,streaming"

def create_spotify():
  auth_manager = SpotifyOAuth(client_id=app_id, client_secret=app_secret, redirect_uri="http://localhost:8888", scope=scope, open_browser=False)

  spotify = spotipy.Spotify(auth_manager=auth_manager)

  return auth_manager, spotify

def fetch_config(config_path):
  global app_id
  global app_secret
  global user_id
  global playlist_id
  global bathplayer_name

  configSection = "DEFAULT"
  Config = configparser.ConfigParser()
  Config.read(config_path)

  app_id = Config.get(configSection, 'app_id')
  app_secret = Config.get(configSection, 'app_secret')
  user_id = Config.get(configSection, 'user_id')
  playlist_id = Config.get(configSection, 'playlist_id')
  bathplayer_name = Config.get(configSection, 'bathplayer_name')

def parse_args():
  global args
  global playing_duration
  parser = argparse.ArgumentParser(description='Bathbuddy is you smart Bathroombuddy')
  parser.add_argument('-c','--configPath', help='Path to configfile', required=True)
  parser.add_argument('-d','--duration', help='Duration to play music', required=True)
  parser.add_argument('-s','--stop', help='Stop Music', required=False)
  args = vars(parser.parse_args())
  playing_duration = int(args['duration'])



if __name__ == '__main__':

  parse_args()
  fetch_config(args['configPath'])

  am, sp = create_spotify()

  devices = sp.devices()

  bathplayer_id = ""
  for device in devices['devices']:
    if device['name'] == bathplayer_name:
      bathplayer_id = device['id']
      break

  if 'stop' in args.keys() and args['stop'] is not None:
    print("Stopping music")
    sp.pause_playback(device_id=bathplayer_id)
  else:
    plstr = 'spotify:playlist:' + playlist_id
    offset = 0

    playlist_tracks = []

    while True:
      response = sp.playlist_items(plstr, offset=offset, fields='items.track.id,total', additional_types=['track'])

      if len(response['items']) == 0:
          break

      for track in response['items']:
        id = "spotify:track:" + track['track']['id']
        playlist_tracks.append(id)
  #      print("added track: ", id)
      offset = offset + len(response['items'])
  #    print(offset, "/", response['total'])

    random.shuffle(playlist_tracks)

    print("playing music for " + str(playing_duration) + " seconds")

    sp.start_playback(device_id=bathplayer_id,uris=playlist_tracks)

    if playing_duration > 0:
      sleep(playing_duration)
      sp.pause_playback(device_id=bathplayer_id)

# Bathbuddy

Bathbuddy is you smart buddy to help you catch the nice time for handwashing and teeth washing. Additionally it makes this time great by supporting you with music.


## Requirements

A registered App at "https://developer.spotify.com/" you will need the clientid and the client secret.
A Spotify Premium Account
A Device registered at spotify to play the music on. Here I suggest using spotifyd.
Maybe a Raspberry Pi with hifiberry oder some music box connected

## The Webapp (folder docker)

* Setup a raspi with raspbian and install docker with docker-compose (execute the following as root):

      curl -sSL https://get.docker.com | sh
      apt install libffi-dev libssl-dev python3-dev python3 python3-pip
      pip3 install docker-compose

* Create the configurations (for examples see ***docker/config/*** folder in this repo)
  * When you are finished you will have at least a config for spotifyd and a settings.cfg for the bathbuddy webapp

* Now its time to create the .cache file for spotipy used by bathbuddy:
  * First we start the container using docker run, to make the first login for your app:

        ~# run "docker run -it -v /path/to/settings.cfg:/app/settings.cfg romulusai/bathbuddy:0.1"

        Go to the following URL: https://accounts.spotify.com/authorize?client_id=123456978&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8888&scope=playlist-read-collaborative+playlist-read-private+streaming+user-modify-playback-state+user-read-playback-state
        Enter the URL you were redirected to: http://localhost:8888/?code=SOMECODE
        * Serving Flask app 'app' (lazy loading)
        * Environment: production
          WARNING: This is a development server. Do not use it in a production deployment.
          Use a production WSGI server instead.
        * Debug mode: on
        * Running on all addresses (0.0.0.0)
          WARNING: This is a development server. Do not use it in a production deployment.
        * Running on http://127.0.0.1:5000
        * Running on http://172.17.0.2:5000 (Press CTRL+C to quit)
        * Restarting with stat
        * Debugger is active!
        * Debugger PIN: 123-454-321
  * If the redirect is not working, no problem, just copy the URL from your browser to the commandline and hit enter, afterwards the app should start as you can see.
  * When the app is registered in your spotify account, we login to the container and copy the .cache file to our config directory on the host:

        #~ docker exec -it a5d1017fd568 bash
        #~ cat .cache
        {"access_token": "XXX", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "XXX", "scope": "playlist-read-collaborative playlist-read-private streaming user-modify-playback-state user-read-playback-state", "expires_at": 1651239579}
  * Copy paste the content of .cache to your host and stop the container again

* Now that we have all our config, we can run everything by executing **docker-compose up -d**

To test it, go to "http://RASPIIP:5000/infinite", it should start the music. Execute the request again and the music should stop.

## The ESP Component (folder bathbuddy)

The ESP Component is like the remote for our musicbox. It is the one who reacts if the soap dispenser is pressed or any other button is pressed.

The Project for the ESP is made for either an ESP8266 Nodemcu or a ESP8266-01S. I use platform IO for the project, which makes the management of secrets a bit easier than Arduino IDE.

What you need is yus an ESP8266 and 3 Buttons connected to them (as described in the pictures). May configure the PINs for the Buttons at the beginning of main.cpp and the flash you ESP with it.

Thats it. When you press a Button, the ESP should send a get Request to the bathbuddy-webapp and the webapp should start playing music.

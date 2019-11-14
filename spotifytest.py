import spotipy
import spotipy.util as util
username = "osteha"
scope = "user-modify-playback-state user-read-playback-state"
client="8a04f930f4c34b3e9be7280ae09a02ba"
secret="194f9fbcb9044e92ba28462d8c69b59d"
token=util.prompt_for_user_token(username,scope,client_id=client,client_secret=secret,redirect_uri="http://localhost/")
sp = spotipy.Spotify(auth=token,requests_session=True)
sp.current_playback()
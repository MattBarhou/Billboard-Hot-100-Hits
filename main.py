import os
from pprint import pprint
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import datetime
from dotenv import load_dotenv

load_dotenv()
Client_ID = os.environ['CLIENT_ID']
Secret = os.environ['SECRET']
description = 'A playlist for all hits on the Billboard 100 on the given date'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=Client_ID,
                                               client_secret=Secret,
                                               redirect_uri="http://example.com",
                                               scope="playlist-modify-private"))
## Get the user id
user = sp.current_user()
user_id = user['id']


def get_song_uris(song_names):
    uris = []
    print('Please wait...')
    for song in song_names:
        # Search for the song
        result = sp.search(q=song, limit=1)
        if result['tracks']['items']:
            # Get the URI of the first track found
            uris.append(result['tracks']['items'][0]['uri'])
        else:
            print(f"Song '{song}' not found on Spotify.")
    print('Successfully added tracks!')
    return uris


def validate(date_text):
    try:
        datetime.date.fromisoformat(date_text)
        return True
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


chosen_date = input('Which year would you like to travel to? Enter a date in the following format: YYYY-MM-DD\n')

# first check if the date is valid, then continue
if validate(chosen_date):
    url = f'https://www.billboard.com/charts/hot-100/{chosen_date}/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # select all the song titles from the hot 100 for the specified date
    song_titles = soup.select('li > #title-of-a-story')
    formatted_titles = [title.text.strip() for title in song_titles]
    song_uris = get_song_uris(formatted_titles)

    ## Create a playlist for the user
    playlist_info = sp.user_playlist_create(user_id, f'{chosen_date} Billboard 100', public=False, description=description)

    # Get the playlist id from the dictionary
    playlist_id = playlist_info['id']

    ## Add tracks to the playlist
    sp.playlist_add_items(playlist_id, song_uris, None)

from InquirerPy import inquirer
from sclib import SoundcloudAPI, Track, Playlist
from utils import *

API = SoundcloudAPI()

def downloader(x: Track | Playlist):	
	if type(x) is Track:
		track = x
		print(f"SoundCloud Track: \033[1m{track.title}")

		title = inquirer.text("title:", default=track.title, validate=required, invalid_message="Title is required", amark="✓").execute()
		artist = inquirer.text("artist:", default=track.artist, amark="✓").execute()
		filename = inquire_filename(sanitize_filename(f"{title} - {artist}")).execute()

		with spinner("Downloading...") as bar:

			with open(f"{filename}.mp3", "wb+") as file:
				track.write_mp3_to(file)
			
			modify_id3(f"{filename}.mp3", title, artist)
			
			bar.title = "Finished!"
	
	elif type(x) is Playlist:
		playlist = x
		print(f"SoundCloud Playlist: \033[1m{playlist.title} ({playlist.track_count} tracks)")

		dir = inquirer.text("target directory:", default=playlist.title, validate=required, invalid_message="Directory is required", amark="✓").execute()
		if not os.path.exists(dir):
			os.mkdir(dir)

		with alive_bar(playlist.track_count, title="Downloading...", length=40, bar="smooth") as bar:

			for track in playlist.tracks:
				
				filename = sanitize_filename(track.title)
				with open(f"{dir}/{filename}.mp3", "wb+") as file:
					track.write_mp3_to(file)
				
				bar()
			
			bar.title = "Finished!"
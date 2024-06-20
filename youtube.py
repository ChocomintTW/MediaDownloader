import re, os
from InquirerPy import inquirer
from pytube import YouTube, Playlist
from alive_progress import alive_bar
from utils import *

from pytube.innertube import _default_clients
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def get_resolutions_list(video: YouTube):
	lst = list(set([stream.resolution for stream in video.streams.filter(only_video=True)]))
	lst.sort(key=lambda res: int(re.search(r'(\d+)', res).group(1)), reverse=True)
	return lst

# downloader
def single_video_downloader(video: YouTube):
	print(f"  >> YouTube Video: \033[1m{video.title}")
	type = inquirer.select("download type:", choices=["mp3", "mp4"], amark="✓").execute()
	
	if type == "mp3":
		title = inquirer.text("title:", default=video.title, validate=required, invalid_message="Title is required", amark="✓").execute()
		artist = inquirer.text("artist:", default=video.author, amark="✓").execute()
		filename = inquire_filename(sanitize_filename(f"{title} - {artist}")).execute()

		with spinner("Downloading...") as bar:
			video.streams.filter().get_audio_only().download(filename="temp.mp3")
			
			bar.title = "Fixing header..."

			ffmpeg_fix_mp3_header("temp.mp3", f"{filename}.mp3")
			os.remove("temp.mp3")
			modify_id3(f"{filename}.mp3", title, artist)

			bar.title = "Finished!"
	
	elif type == "mp4":
		with spinner("Fetching resolutions...") as bar:
			resolution_list = get_resolutions_list(video)
			bar.title = "Fetching resolutions - Done."
		
		resolution: str = inquirer.select("resolution:", choices=resolution_list, amark="✓").execute()
		filename = inquire_filename(sanitize_filename(video.title)).execute()

		with spinner("Downloading...") as bar:
			video.streams.filter(res=resolution).first().download(filename=f"{filename}.mp4")
			bar.title = "Finished!"

def playlist_downloader(playlist: Playlist):
	tracks_count = len(playlist.videos)
	print(f"  >> YouTube Playlist: \033[1m{playlist.title} ({tracks_count} tracks)")

	type = inquirer.select("download type:", choices=["mp3", "mp4"], amark="✓").execute()

	dir = inquirer.text("target directory:", default=playlist.title, validate=required, invalid_message="Directory is required", amark="✓").execute()
	if not os.path.exists(dir):
		os.mkdir(dir)
	
	fix = None
	if type == "mp3":
		fix = inquirer.confirm("fix header:", amark="✓").execute()

	if fix:
		auto_add = inquirer.confirm("auto add title & artist:", default=True, amark="✓").execute()

	with alive_bar(tracks_count, title="Downloading...", length=40, bar="smooth") as bar:
		
		for video in playlist.videos:
			filename = sanitize_filename(video.title)
			
			if type == "mp3":
				if fix:
					video.streams.filter().get_audio_only().download(filename="temp.mp3")
					ffmpeg_fix_mp3_header("temp.mp3", f"{dir}/{filename}.mp3")
					os.remove("temp.mp3")

					if auto_add:
						modify_id3(f"{dir}/{filename}.mp3", video.title, video.author)

				else:
					video.streams.filter().get_audio_only().download(filename=f"{dir}/{filename}.mp3")
			
			elif type == "mp4":
				video.streams.filter().get_highest_resolution().download(filename=f"{dir}/{filename}.mp4")
			
			bar()
		
		bar.title = "Finished!"
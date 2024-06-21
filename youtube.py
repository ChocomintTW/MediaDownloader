import re, os
from InquirerPy import inquirer
from pytube import YouTube, Playlist
from utils import *

from pytube.innertube import _default_clients
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def get_resolutions_list(video: YouTube):
	lst = list(set([stream.resolution for stream in video.streams.filter(only_video=True)]))
	lst.sort(key=lambda res: int(re.search(r'(\d+)', res).group(1)), reverse=True)
	return lst

# downloader
def single_video_downloader(video: YouTube, having_ffmpeg: bool):
	print(f"  >> YouTube Video: \033[1m{video.title}")
	type = inquirer.select("download type:", choices=["mp3", "mp4"], amark="✓").execute()
	
	if type == "mp3":
		if not having_ffmpeg:
			filename = inquire_filename(sanitize_filename(f"{video.title} - {video.author}")).execute()

			with spinner("Downloading...") as bar:
				video.streams.filter().get_audio_only().download(filename=f"{filename}.mp3")
				bar.title = "Finished!"

		else:
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


def playlist_downloader(playlist: Playlist, having_ffmpeg: bool):
	tracks_count = len(playlist.videos)
	print(f"  >> YouTube Playlist: \033[1m{playlist.title} ({tracks_count} tracks)")

	type = inquirer.select("download type:", choices=["mp3", "mp4"], amark="✓").execute()

	selected_videos, selected_count = inquire_playlist_range(playlist.videos)

	dir = inquirer.text("target directory:", default=playlist.title, validate=required, invalid_message="Directory is required", amark="✓").execute()
	if not os.path.exists(dir):
		os.mkdir(dir)
	
	fix = None
	if type == "mp3" and having_ffmpeg:
		fix = inquirer.confirm("fix header:", amark="✓").execute()

	if fix:
		auto_add = inquirer.confirm("auto add title & artist:", default=True, amark="✓").execute()
	
	format = inquire_filename_format()

	with playlist_downloading_bar(selected_count) as bar:
		
		number = 1
		for video in selected_videos:
			filename = sanitize_filename(playlist_filename_replace(format, number, video.title, video.author))
			
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
			number += 1
		
		bar.title = "Finished!"
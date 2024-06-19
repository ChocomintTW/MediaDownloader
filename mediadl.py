import re, ssl
from InquirerPy import inquirer
from pytube import YouTube, Playlist
from utils import *

import youtube
import soundcloud

def is_yt_video(link: str):
	return re.match(r"https:\/\/www\.youtube\.com\/watch\?v=[\w_-]{11}(&list=[\w_-]{34}&index=[0-9]+)?", link)

def is_yt_playlist(link: str):
	return re.match(r"https:\/\/www\.youtube\.com\/playlist\?list=[\w_-]{34}", link)

def is_soundcloud(link: str):
	return link.startswith("https://soundcloud.com/")

def link_validator(link: str):
	is_yt = link.startswith("https://www.youtube.com/")
	is_sc = is_soundcloud(link)
	
	return is_yt or is_sc

# main
def main():
	ssl._create_default_https_context = ssl._create_stdlib_context

	print("Media Downloader v1.0 - By Chocomint\n")

	link = inquirer.text(
		"media link:",
		validate=link_validator,
		invalid_message="Only support Youtube and SoundCloud",
		amark="✓"
	).execute()

	if is_yt_video(link):
		try:
			video = YouTube(link)
		except:
			error("Invalid YouTube video")
			return
		
		youtube.single_video_downloader(video)

	elif is_yt_playlist(link):
		try:
			playlist = Playlist(link)
		except:
			error("Invalid YouTube playlist")
			return
		
		youtube.playlist_downloader(playlist)

	elif is_soundcloud(link):
		block_print_error()
		try:
			with spinner("Resolving SoundCloud...") as bar:
				x = soundcloud.API.resolve(link)
				bar.title = "Resolving SoundCloud - Done."
		except:
			error("Invalid SoundCloud link")
			bar.title = "Resolved error."
			enable_print_error()
			return
		
		enable_print_error()

		soundcloud.downloader(x)

	else:
		error("Invalid link")
		return

if __name__ == "__main__":
	main()

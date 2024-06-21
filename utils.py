import re, subprocess, sys, os
from InquirerPy import inquirer
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from alive_progress import alive_bar
from colorama import Fore, Style

def spinner(title):
	return alive_bar(title=title, unknown="brackets", length=8, spinner="classic", monitor=False, stats=False)

def playlist_downloading_bar(total: int):
	return alive_bar(total, title="Downloading...", length=40, bar="notes")

def ffmpeg_fix_mp3_header(input_path: str, output_path: str):
	subprocess.run(f"ffmpeg -loglevel error -i {input_path} -vn -ar 44100 -ac 2 -b:a 192k \"{output_path}\"", check=True)

def modify_id3(filename: str, title: str, artist: str):
	audio = MP3(filename, ID3=EasyID3)
	audio["title"]  = title
	audio["artist"] = artist
	audio.save()

INVALID_CHARS = r"[<>:\"/\\|?*]"

def validate_filename(filename: str):
	return not re.search(INVALID_CHARS, filename)

def sanitize_filename(filename: str):
	sanitized_filename = re.sub(INVALID_CHARS, '_', filename)
	return sanitized_filename

def inquire_filename(default: str):
	return inquirer.text(
		"filename:",
		default=default,
		validate=validate_filename,
		invalid_message="Filename should not contain these characters: \\ / : * ? \" < > |",
		amark="✓"
	)

def required(string: str):
	return string != ""

def error(message: str):
	print(Fore.RED + "[X] " + message + Style.RESET_ALL)

def warning(message: str):
	print(Fore.YELLOW + "[!] " + message + Style.RESET_ALL)

def block_print_error():
	sys.stderr = open(os.devnull, "w")

def enable_print_error():
	sys.stderr = sys.__stderr__

def validate_range(range_string: str, max: int):
	if range_string == "all":
		return True
	
	if not re.match(r"\d*-\d*", range_string):
		return False
	
	from_index, to_index = range_string.split("-")
	return 1 <= int(from_index) <= int(to_index) <= max

def inquire_playlist_range(playlist: list):
	count = len(playlist)

	selected_range = inquirer.text(
		"select range:",
		default="all",
		validate=lambda x: validate_range(x, count),
		invalid_message="Range should match \"number-number\" and be less than max tracks",
		amark="✓"
	).execute()

	if selected_range == "all":
		from_index, to_index = 1, count
	else:
		from_index, to_index = selected_range.split("-")
		from_index = int(from_index)
		to_index = int(to_index)
	
	return playlist[from_index-1:to_index], to_index - from_index + 1

def inquire_filename_format():
	warning("Support variables: %num%, %title%, %artist%")
	return inquirer.text(
		"filename format:",
		default="%title% - %artist%",
	).execute()

def playlist_filename_replace(format: str, num: int, title: str, artist: str):
	return format.replace("%num%", str(num)).replace("%title%", title).replace("%artist%", artist)
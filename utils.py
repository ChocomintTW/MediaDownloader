import re, subprocess, sys, os
from InquirerPy import inquirer
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from alive_progress import alive_bar
from colorama import Fore, Style

def spinner(title):
	return alive_bar(title=title, unknown="brackets", length=8, spinner="classic", monitor=False, stats=False)

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
		invalid_message=f"Filename should not contain these characters: \\ / : * ? \" < > |",
		amark="✓"
	)

def required(string: str):
	return string != ""

def error(message: str):
	print(Fore.RED + message + Style.RESET_ALL)

def block_print_error():
	sys.stderr = open(os.devnull, "w")

def enable_print_error():
	sys.stderr = sys.__stderr__
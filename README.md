# Audio Converter
Convert Files between flac,mp3,m4a,ogg,opus,wav. Preserves Metadata and Embedded Lyrics.

## Requirements

- FFMPEG
- Python 3.10+
- mutagen
- tqdm

## Installation

- clone/download the repo
- `pip install ffmpeg mutagen tqdm`
- cd `<YOUR_PATH_TO>/audio_converter`

## How to use?

- Open Terminal <sub><sub><sub>cancer</sub></sub></sub>
- Type: `python convert_audio.py Source_Folder_Path Destination_Folder_Path File_Type`
- Done, your files are served!
- All known failures are logged in `conversion_failures.txt` as human readable text.

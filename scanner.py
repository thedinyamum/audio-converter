"""
scanner.py
Recursively scan a music library for supported audio files.
"""

from pathlib import Path

AUDIO_EXTS = {
    ".flac", ".mp3", ".m4a", ".aac",
    ".ogg", ".opus", ".wav",
}

def scan(folder):
    folder = Path(folder).expanduser().resolve()
    if not folder.exists():
        raise FileNotFoundError(folder)

    files = [
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    ]
    files.sort()
    return files

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scan a music library.")
    parser.add_argument("folder")
    args = parser.parse_args()

    songs = scan(args.folder)
    print(f"Found {len(songs)} songs.\n")
    for song in songs:
        print(song)

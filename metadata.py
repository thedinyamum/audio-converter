"""
metadata.py

Read/write common audio metadata.
"""

from pathlib import Path

from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.id3 import (
    ID3,
    TIT2,
    TPE1,
    TALB,
    TPE2,
    TRCK,
    TPOS,
    TCON,
    TDRC,
)


FIELDS = (
    "title",
    "artist",
    "album",
    "albumartist",
    "tracknumber",
    "discnumber",
    "genre",
    "date",
    "comment",
)


def _first(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def read_tags(path):
    audio = File(path, easy=True)

    if audio is None:
        raise ValueError(path)

    return {
        key: _first(audio.get(key))
        for key in FIELDS
    }


def write_tags(path, tags):
    path = Path(path)
    ext = path.suffix.lower()

    ############################################################
    # FLAC
    ############################################################

    if ext == ".flac":

        audio = FLAC(path)
        audio.clear()

        mapping = {
            "title": "TITLE",
            "artist": "ARTIST",
            "album": "ALBUM",
            "albumartist": "ALBUMARTIST",
            "tracknumber": "TRACKNUMBER",
            "discnumber": "DISCNUMBER",
            "genre": "GENRE",
            "date": "DATE",
            "comment": "COMMENT",
        }

        for src, dst in mapping.items():

            value = tags.get(src)

            if value is not None:
                audio[dst] = [str(value)]

        audio.save()
        return

    ############################################################
    # M4A / MP4
    ############################################################

    if ext == ".m4a":

        audio = MP4(path)
        audio.clear()

        mapping = {
            "title": "\xa9nam",
            "artist": "\xa9ART",
            "album": "\xa9alb",
            "albumartist": "aART",
            "genre": "\xa9gen",
            "date": "\xa9day",
            "comment": "\xa9cmt",
        }

        for src, dst in mapping.items():

            value = tags.get(src)

            if value is not None:
                audio[dst] = [str(value)]

        value = tags.get("tracknumber")

        if value is not None:
            audio["trkn"] = [
                (
                    int(str(value).split("/")[0]),
                    0,
                )
            ]

        value = tags.get("discnumber")

        if value is not None:
            audio["disk"] = [
                (
                    int(str(value).split("/")[0]),
                    0,
                )
            ]

        audio.save()
        return

    ############################################################
    # MP3
    ############################################################

    if ext == ".mp3":

        try:
            audio = ID3(path)
            audio.delete()
        except Exception:
            pass

        audio = ID3()

        frames = {
            "title": TIT2,
            "artist": TPE1,
            "album": TALB,
            "albumartist": TPE2,
            "tracknumber": TRCK,
            "discnumber": TPOS,
            "genre": TCON,
            "date": TDRC,
        }

        for key, frame in frames.items():

            value = tags.get(key)

            if value is not None:
                audio.add(
                    frame(
                        encoding=3,
                        text=str(value),
                    )
                )

        # Save to the destination file.
        audio.save(path)

        return

    raise ValueError(f"Unsupported format: {ext}")


if __name__ == "__main__":

    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser()

    parser.add_argument("file")

    args = parser.parse_args()

    pprint(read_tags(args.file))

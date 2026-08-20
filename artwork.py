"""
artwork.py

Extract and embed album artwork across common audio formats.
"""

from pathlib import Path

from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, APIC
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
import base64


def extract(path):
    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".flac":
        audio = FLAC(path)
        if audio.pictures:
            pic = audio.pictures[0]
            return {
                "data": pic.data,
                "mime": pic.mime,
                "type": pic.type,
            }

    elif ext == ".mp3":
        audio = ID3(path)
        for frame in audio.getall("APIC"):
            return {
                "data": frame.data,
                "mime": frame.mime,
                "type": frame.type,
            }

    elif ext == ".m4a":
        audio = MP4(path)
        covers = audio.tags.get("covr")
        if covers:
            cover = covers[0]
            mime = "image/png" if cover.imageformat == MP4Cover.FORMAT_PNG else "image/jpeg"
            return {
                "data": bytes(cover),
                "mime": mime,
                "type": 3,
            }

    elif ext in (".ogg", ".opus"):
        audio = OggVorbis(path) if ext == ".ogg" else OggOpus(path)
        pic = audio.get("metadata_block_picture")
        if pic:
            return {
                "data": base64.b64decode(pic[0]),
                "mime": None,
                "type": 3,
            }

    return None


def embed(path, artwork):
    if artwork is None:
        return False

    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".flac":
        audio = FLAC(path)
        audio.clear_pictures()
        pic = Picture()
        pic.data = artwork["data"]
        pic.mime = artwork["mime"] or "image/jpeg"
        pic.type = artwork.get("type", 3)
        audio.add_picture(pic)
        audio.save()
        return True

    if ext == ".mp3":
        audio = ID3(path)
        audio.delall("APIC")
        audio.add(APIC(
            encoding=3,
            mime=artwork["mime"] or "image/jpeg",
            type=artwork.get("type", 3),
            desc="Cover",
            data=artwork["data"],
        ))
        audio.save()
        return True

    if ext == ".m4a":
        audio = MP4(path)
        fmt = MP4Cover.FORMAT_PNG if (artwork["mime"] or "").endswith("png") else MP4Cover.FORMAT_JPEG
        audio["covr"] = [MP4Cover(artwork["data"], imageformat=fmt)]
        audio.save()
        return True

    # OGG/Opus writing intentionally deferred until formats.py
    return False


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("file")
    args = p.parse_args()

    art = extract(args.file)
    if art:
        print(f"Artwork found ({len(art['data'])} bytes)")
    else:
        print("No artwork")

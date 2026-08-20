"""
lyrics.py

Read and write embedded lyrics across common audio formats.
Returns plain/synced text exactly as stored.
"""

from pathlib import Path

from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, USLT, SYLT
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus


def extract(path):
    path=Path(path)
    ext=path.suffix.lower()

    if ext==".flac":
        a=FLAC(path)
        return a.get("LYRICS",[None])[0]

    if ext==".m4a":
        a=MP4(path)
        return a.tags.get("\xa9lyr",[None])[0]

    if ext==".mp3":
        a=ID3(path)
        for f in a.getall("SYLT"):
            if isinstance(f,SYLT):
                return "\n".join(t for t,_ in f.text)
        for f in a.getall("USLT"):
            if isinstance(f,USLT):
                return f.text
        return None

    if ext==".ogg":
        a=OggVorbis(path)
        return a.get("LYRICS",[None])[0]

    if ext==".opus":
        a=OggOpus(path)
        return a.get("LYRICS",[None])[0]

    return None


def embed(path,lyrics,synced=True):
    path=Path(path)
    ext=path.suffix.lower()

    if ext==".flac":
        a=FLAC(path)
        a["LYRICS"]=[lyrics]
        a.save()
        return True

    if ext==".m4a":
        a=MP4(path)
        a["\xa9lyr"]=[lyrics]
        a.save()
        return True

    if ext==".mp3":
        a=ID3(path)
        a.delall("USLT")
        a.delall("SYLT")
        a.add(USLT(encoding=3,lang="eng",desc="",text=lyrics))
        a.save()
        return True

    if ext==".ogg":
        a=OggVorbis(path)
        a["LYRICS"]=[lyrics]
        a.save()
        return True

    if ext==".opus":
        a=OggOpus(path)
        a["LYRICS"]=[lyrics]
        a.save()
        return True

    return False


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("file")
    a=p.parse_args()
    print(extract(a.file))

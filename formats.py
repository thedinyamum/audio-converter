"""
formats.py

Central format-specific metadata mappings.
"""

VORBIS_WRITE_MAP = {
    "title": "TITLE",
    "artist": "ARTIST",
    "album": "ALBUM",
    "albumartist": "ALBUMARTIST",
    "tracknumber": "TRACKNUMBER",
    "discnumber": "DISCNUMBER",
    "genre": "GENRE",
    "date": "DATE",
    "comment": "COMMENT",
    "lyrics": "LYRICS",
}

MP4_WRITE_MAP = {
    "title": "\xa9nam",
    "artist": "\xa9ART",
    "album": "\xa9alb",
    "albumartist": "aART",
    "genre": "\xa9gen",
    "date": "\xa9day",
    "comment": "\xa9cmt",
    "lyrics": "\xa9lyr",
}

ID3_WRITE_MAP = {
    "title": "TIT2",
    "artist": "TPE1",
    "albumartist": "TPE2",
    "album": "TALB",
    "tracknumber": "TRCK",
    "discnumber": "TPOS",
    "genre": "TCON",
    "date": "TDRC",
    "lyrics": "USLT",
}

REPLAYGAIN = (
    "REPLAYGAIN_TRACK_GAIN",
    "REPLAYGAIN_TRACK_PEAK",
    "REPLAYGAIN_ALBUM_GAIN",
    "REPLAYGAIN_ALBUM_PEAK",
)

MUSICBRAINZ = (
    "MUSICBRAINZ_TRACKID",
    "MUSICBRAINZ_ARTISTID",
    "MUSICBRAINZ_ALBUMID",
    "MUSICBRAINZ_RELEASEGROUPID",
)


def normalize_key(key):
    return key.strip().upper()


def is_replaygain(key):
    return normalize_key(key) in REPLAYGAIN


def is_musicbrainz(key):
    return normalize_key(key) in MUSICBRAINZ

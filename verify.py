"""
verify.py

Verify that a converted file retained important properties.
"""

from pathlib import Path

from mutagen import File

from metadata import read_tags
from lyrics import extract as extract_lyrics
from artwork import extract as extract_artwork


IGNORE_FIELDS = {
    "comment",
}


def normalize(value):
    """
    Normalize metadata values so equivalent values compare equal.
    """

    if value is None:
        return ""

    if isinstance(value, (list, tuple)):
        if not value:
            return ""
        value = value[0]

    return str(value).strip()


def _audio_info(path):
    audio = File(path)

    if audio is None:
        raise ValueError(f"Unsupported file: {path}")

    info = audio.info

    return {
        "duration": round(getattr(info, "length", 0), 2),
        "sample_rate": getattr(info, "sample_rate", None),
        "channels": getattr(info, "channels", None),
        "bitrate": getattr(info, "bitrate", None),
    }


def verify(source, destination, duration_tolerance=0.10):
    """
    Returns:

        (success, report)
    """

    source = Path(source)
    destination = Path(destination)

    report = {
        "exists": destination.exists(),
        "metadata": False,
        "lyrics": False,
        "artwork": False,
        "duration": False,
        "sample_rate": False,
        "channels": False,
    }

    if not destination.exists():
        return False, report

    ############################################################
    # Audio properties
    ############################################################

    src_info = _audio_info(source)
    dst_info = _audio_info(destination)

    report["duration"] = (
        abs(src_info["duration"] - dst_info["duration"])
        <= duration_tolerance
    )

    report["sample_rate"] = (
        src_info["sample_rate"]
        == dst_info["sample_rate"]
    )

    report["channels"] = (
        src_info["channels"]
        == dst_info["channels"]
    )

    ############################################################
    # Metadata
    ############################################################

    src_tags = read_tags(source)
    dst_tags = read_tags(destination)

    report["metadata"] = all(
        normalize(src_tags.get(field))
        ==
        normalize(dst_tags.get(field))
        for field in (
            set(src_tags)
            |
            set(dst_tags)
        )
        if field not in IGNORE_FIELDS
    )

    ############################################################
    # Lyrics
    ############################################################

    src_lyrics = extract_lyrics(source)
    dst_lyrics = extract_lyrics(destination)

    report["lyrics"] = (
        normalize(src_lyrics)
        ==
        normalize(dst_lyrics)
    )

    ############################################################
    # Artwork
    ############################################################

    src_art = extract_artwork(source)
    dst_art = extract_artwork(destination)

    if src_art is None and dst_art is None:

        report["artwork"] = True

    elif src_art is not None and dst_art is not None:

        report["artwork"] = (
            src_art["data"]
            ==
            dst_art["data"]
        )

    ############################################################

    success = all(report.values())

    return success, report


if __name__ == "__main__":

    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser(
        description="Verify converted audio."
    )

    parser.add_argument("source")
    parser.add_argument("destination")

    args = parser.parse_args()

    ok, report = verify(
        args.source,
        args.destination,
    )

    print("PASS" if ok else "FAIL")
    pprint(report)

"""
converter.py

Audio conversion backend using FFmpeg.
This module only converts audio. Metadata, artwork and lyrics
are copied by other modules after conversion.
"""

from pathlib import Path
import subprocess

SUPPORTED = {
    "flac": [".flac"],
    "m4a": [".m4a", ".mp4"],
    "mp3": [".mp3"],
    "ogg": [".ogg"],
    "opus": [".opus"],
    "wav": [".wav"],
}


def output_path(src: Path, src_root: Path, dst_root: Path, fmt: str) -> Path:
    rel = src.relative_to(src_root)
    return (dst_root / rel).with_suffix("." + fmt)


def ffmpeg_args(fmt: str):
    fmt = fmt.lower()

    if fmt == "flac":
        return ["-c:a", "flac"]

    if fmt == "m4a":
        return ["-c:a", "aac", "-b:a", "320k"]

    if fmt == "mp3":
        return ["-c:a", "libmp3lame", "-q:a", "0"]

    if fmt == "ogg":
        return ["-c:a", "libvorbis", "-q:a", "8"]

    if fmt == "opus":
        return ["-c:a", "libopus", "-b:a", "192k"]

    if fmt == "wav":
        return ["-c:a", "pcm_s24le"]

    raise ValueError(f"Unsupported output format: {fmt}")


def convert(src: Path, src_root: Path, dst_root: Path, fmt: str, overwrite=False):
    src = Path(src)
    dst = output_path(src, src_root, dst_root, fmt)

    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists() and not overwrite:
        return dst, "skipped"

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",

        "-i",
        str(src),

        # Only convert audio
        "-map",
        "0:a:0",

        # Don't copy metadata
        "-map_metadata",
        "-1",

        # Don't copy chapters
        "-map_chapters",
        "-1",

        *ffmpeg_args(fmt),

        str(dst),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return dst, "converted"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert a single audio file.")
    parser.add_argument("input")
    parser.add_argument("source_root")
    parser.add_argument("destination_root")
    parser.add_argument("format")
    parser.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()

    out, status = convert(
        Path(args.input),
        Path(args.source_root),
        Path(args.destination_root),
        args.format,
        overwrite=args.overwrite,
    )

    print(status, out)

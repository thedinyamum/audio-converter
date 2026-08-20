"""
utils.py

Shared utility functions for the audio converter.
"""

from pathlib import Path
import shutil
import hashlib


def ensure_parent(path):
    """
    Create parent directories if necessary.
    """
    Path(path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def preserve_structure(
    source,
    source_root,
    destination_root,
    new_extension=None,
):
    """
    Preserve folder structure while optionally changing extension.
    """

    source = Path(source)
    source_root = Path(source_root)
    destination_root = Path(destination_root)

    relative = source.relative_to(source_root)

    output = destination_root / relative

    if new_extension:
        output = output.with_suffix(
            "." + new_extension.lower().lstrip(".")
        )

    ensure_parent(output)

    return output


def file_sha256(
    filename,
    chunk_size=1024 * 1024,
):
    """
    SHA256 checksum.
    """

    h = hashlib.sha256()

    with open(filename, "rb") as f:

        while True:

            chunk = f.read(chunk_size)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def copy_file(
    source,
    destination,
    overwrite=False,
):
    """
    Copy file preserving timestamps.
    """

    source = Path(source)
    destination = Path(destination)

    ensure_parent(destination)

    if destination.exists() and not overwrite:
        return False

    shutil.copy2(
        source,
        destination,
    )

    return True


def format_bytes(size):

    units = (
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    )

    size = float(size)

    for unit in units:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def format_seconds(seconds):

    seconds = int(seconds)

    hours, seconds = divmod(
        seconds,
        3600,
    )

    minutes, seconds = divmod(
        seconds,
        60,
    )

    if hours:
        return f"{hours:d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:d}:{seconds:02d}"


def safe_filename(name):
    """
    Remove characters illegal on Windows/macOS/Linux.
    """

    illegal = '<>:"/\\|?*'

    for c in illegal:
        name = name.replace(c, "_")

    return name.strip()


def is_audio(path):

    return (
        Path(path).suffix.lower()
        in {
            ".flac",
            ".mp3",
            ".m4a",
            ".aac",
            ".ogg",
            ".opus",
            ".wav",
        }
    )


if __name__ == "__main__":

    print(
        preserve_structure(
            "/Music/A/B/song.flac",
            "/Music",
            "/Converted",
            "m4a",
        )
    )

    print(
        format_bytes(123456789)
    )

    print(
        format_seconds(5023)
    )

    print(
        safe_filename(
            'My:Song?*.flac'
        )
    )

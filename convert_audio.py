#!/usr/bin/env python3

"""
convert_audio.py

Main entry point for the audio converter.
"""

import argparse
import time
from pathlib import Path

from scanner import scan
from converter import convert
from metadata import read_tags, write_tags
from lyrics import extract as extract_lyrics
from lyrics import embed as embed_lyrics
from artwork import extract as extract_artwork
from artwork import embed as embed_artwork
from verify import verify
from worker import process_batch, write_failure_report
from utils import preserve_structure


def process_factory(
    source_root,
    destination_root,
    output_format,
    overwrite=False,
):
    """
    Creates the worker callback.
    """

    source_root = Path(source_root)
    destination_root = Path(destination_root)

    def process(source):

        start = time.perf_counter()

        destination = preserve_structure(
            source,
            source_root,
            destination_root,
            output_format,
        )

        try:

            converted_file, status = convert(
                source,
                source_root,
                destination_root,
                output_format,
                overwrite=overwrite,
            )

            if status == "skipped":

                return {
                    "status": "skipped",
                    "source": source,
                    "destination": converted_file,
                    "verified": True,
                    "time": time.perf_counter() - start,
                    "error": None,
                }

            #################################################
            # Metadata
            #################################################

            tags = read_tags(source)

            write_tags(
                converted_file,
                tags,
            )

            #################################################
            # Lyrics
            #################################################

            lyrics = extract_lyrics(source)

            if lyrics:

                embed_lyrics(
                    converted_file,
                    lyrics,
                )

            #################################################
            # Artwork
            #################################################

            artwork = extract_artwork(source)

            if artwork:

                embed_artwork(
                    converted_file,
                    artwork,
                )

            #################################################
            # Verification
            #################################################

            success, report = verify(
                source,
                converted_file,
            )

            if not success:

                return {
                    "status": "failed",
                    "source": source,
                    "destination": converted_file,
                    "verified": False,
                    "time": time.perf_counter() - start,
                    "error": f"Verification failed: {report}",
                }

            return {
                "status": "converted",
                "source": source,
                "destination": converted_file,
                "verified": True,
                "time": time.perf_counter() - start,
                "error": None,
            }

        except Exception as e:

            return {
                "status": "failed",
                "source": source,
                "destination": destination,
                "verified": False,
                "time": time.perf_counter() - start,
                "error": str(e),
            }

    return process


def main():

    parser = argparse.ArgumentParser(
        description="Convert an audio library while preserving metadata."
    )

    parser.add_argument(
        "source",
        help="Source music folder",
    )

    parser.add_argument(
        "destination",
        help="Destination folder",
    )

    parser.add_argument(
        "format",
        choices=[
            "flac",
            "mp3",
            "m4a",
            "ogg",
            "opus",
            "wav",
        ],
        help="Output format",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Parallel workers",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files",
    )

    args = parser.parse_args()

    print("\nScanning library...")

    files = scan(args.source)

    print(f"Found {len(files)} audio files.\n")

    process = process_factory(
        args.source,
        args.destination,
        args.format,
        overwrite=args.overwrite,
    )

    report = process_batch(
        files,
        process,
        workers=args.workers,
    )

    stats = report["stats"]

    print("\n")
    print("=" * 60)
    print("Conversion Complete")
    print("=" * 60)

    print(f"Processed : {stats['processed']}")
    print(f"Converted : {stats['converted']}")
    print(f"Skipped   : {stats['skipped']}")
    print(f"Failed    : {stats['failed']}")
    print(f"Verified  : {stats['verified']}")
    print(f"Wall Time : {stats['wall_time']:.2f}s")
    print(f"Avg/File  : {stats['avg_time']:.3f}s")
    print(f"Speed     : {stats['throughput']:.2f} files/sec")

    if report["failures"]:

        write_failure_report(
            report["failures"],
        )

        print(
            f"\nFailure report written "
            f"({len(report['failures'])} failures)"
        )


if __name__ == "__main__":
    main()

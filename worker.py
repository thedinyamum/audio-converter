"""
worker.py

Parallel conversion worker.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from time import perf_counter

from tqdm import tqdm


stats_lock = Lock()


def process_batch(
    files,
    process,
    workers=8,
):
    """
    process(file) should return:

    {
        "status": "converted" | "skipped" | "failed",
        "source": Path,
        "destination": Path | None,
        "verified": bool,
        "time": float,
        "error": str | None,
    }
    """

    start = perf_counter()

    stats = {
        "processed": 0,
        "converted": 0,
        "skipped": 0,
        "failed": 0,
        "verified": 0,
        "total_time": 0.0,
    }

    failures = []
    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:

        futures = {
            executor.submit(process, file): file
            for file in files
        }

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            unit="file",
            desc="Converting",
        ):

            source = futures[future]

            try:
                result = future.result()

            except Exception as e:

                result = {
                    "status": "failed",
                    "source": source,
                    "destination": None,
                    "verified": False,
                    "time": 0.0,
                    "error": str(e),
                }

            results.append(result)

            with stats_lock:

                stats["processed"] += 1

                status = result["status"]

                if status == "converted":
                    stats["converted"] += 1

                elif status == "skipped":
                    stats["skipped"] += 1

                else:
                    stats["failed"] += 1

                if result.get("verified"):
                    stats["verified"] += 1

                stats["total_time"] += result.get(
                    "time",
                    0.0,
                )

                if result.get("error"):

                    failures.append(
                        {
                            "source": result["source"],
                            "destination": result["destination"],
                            "error": result["error"],
                        }
                    )

    elapsed = perf_counter() - start

    stats["wall_time"] = elapsed

    stats["avg_time"] = (
        stats["total_time"] / stats["processed"]
        if stats["processed"]
        else 0.0
    )

    stats["throughput"] = (
        stats["processed"] / elapsed
        if elapsed
        else 0.0
    )

    return {
        "stats": stats,
        "results": results,
        "failures": failures,
    }


def write_failure_report(
    failures,
    filename="conversion_failures.txt",
):

    if not failures:
        return

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as f:

        for failure in failures:

            f.write(
                f"{failure['source']}\n"
            )

            if failure["destination"]:
                f.write(
                    f"Destination: "
                    f"{failure['destination']}\n"
                )

            f.write(
                f"Error: "
                f"{failure['error']}\n"
            )

            f.write(
                "-" * 70 + "\n"
            )


if __name__ == "__main__":

    import random
    import time


    def demo(file):

        t0 = perf_counter()

        time.sleep(
            random.uniform(
                0.05,
                0.25,
            )
        )

        if random.random() < 0.08:

            return {
                "status": "failed",
                "source": file,
                "destination": None,
                "verified": False,
                "time": perf_counter() - t0,
                "error": "Random failure",
            }

        return {
            "status": "converted",
            "source": file,
            "destination": f"{file}.flac",
            "verified": True,
            "time": perf_counter() - t0,
            "error": None,
        }


    report = process_batch(
        list(range(100)),
        demo,
    )

    stats = report["stats"]

    print("\nSummary")
    print("=" * 40)

    print(f"Processed : {stats['processed']}")
    print(f"Converted : {stats['converted']}")
    print(f"Skipped   : {stats['skipped']}")
    print(f"Failed    : {stats['failed']}")
    print(f"Verified  : {stats['verified']}")
    print(f"Wall Time : {stats['wall_time']:.2f}s")
    print(f"Avg/File  : {stats['avg_time']:.3f}s")
    print(f"Speed     : {stats['throughput']:.2f} files/sec")

    write_failure_report(report["failures"])

    if report["failures"]:
        print(
            f"\nFailure report written "
            f"({len(report['failures'])} failures)"
        )

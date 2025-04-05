"""
Script to enqueue textbook processing tasks into a Redis-backed queue.

This script reads a list of files (blobs) from a specified Google Cloud Storage
bucket and enqueues tasks for each file, storing metadata such as source path,
instructor, and destination path.

Requires:
- Google Cloud credentials to access GCS.
- A running Redis server accessible via environment variables.
"""

import argparse
from pathlib import Path

from google.cloud import storage
from sources.queue import Queue


def main():
    """
    Main entry point for the task-enqueuing script.

    :param --bucket: Name of the Google Cloud Storage bucket.
    :param --read-prefix: Prefix to filter source files (GCS blobs).
    :param --instructor: Instructor identifier to attach to each task.
    :param --save-prefix: Path prefix for saving processed results.
    """
    parser = argparse.ArgumentParser(description="Queue textbook processing tasks from GCS.")
    parser.add_argument("--bucket", type=str, required=True, help="GCS bucket name.")
    parser.add_argument("--read-prefix", type=str, required=True, help="Prefix for input blobs in the bucket.")
    parser.add_argument("--instructor", type=str, required=True, help="Instructor name or ID.")
    parser.add_argument("--save-prefix", type=str, required=True, help="Output path prefix for saving processed results.")
    parsed = parser.parse_args()

    queue = Queue(topic="textbook")
    store = storage.Client().bucket(parsed.bucket)

    for blob in store.list_blobs(prefix=parsed.read_prefix):
        queue.create({
            "read-from": blob.name,
            "instructor": parsed.instructor,
            "save-into": Path(parsed.save_prefix, Path(blob.name).name).as_posix(),
        })


if __name__ == "__main__":
    main()

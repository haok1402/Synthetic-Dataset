import argparse
from pathlib import Path

from google.cloud import storage
from sources.queue import Queue

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", type=str, required=True)
    parser.add_argument("--read-prefix", type=str, required=True)
    parser.add_argument("--instructor", type=str, required=True)
    parser.add_argument("--save-prefix", type=str, required=True)
    parsed = parser.parse_args()

    store, queue = storage.Client(), Queue("textbook")
    for blob in store.list_blobs(parsed.bucket, prefix=parsed.read_prefix):
        queue.create({
            "read-from": blob.name,
            "instructor": parsed.instructor,
            "save-into": Path(parsed.save_prefix, Path(blob.name).name).as_posix(),
        })

if __name__ == "__main__":
    main()

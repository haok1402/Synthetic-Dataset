import argparse
from pathlib import Path
from sources.textbook import store, queue

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--read-prefix", type=str, required=True)
    parser.add_argument("--save-prefix", type=str, required=True)
    parsed = parser.parse_args()

    for blob in store.list_blobs(prefix=parsed.read_prefix):
        queue.create({
            "model": parsed.model,
            "read-from": blob.name,
            "save-into": Path(parsed.save_prefix, Path(blob.name).name).as_posix(),
        })

if __name__ == "__main__":
    main()

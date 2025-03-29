#!/bin/bash

# Author: Hao Kang
# Date: May 29, 2025

textbook() {
    task=$1

    # Skip if task file is empty (already processed)
    [ ! -s "$task" ] && return 0

    # Read GCS link and local file path
    load_link=$(sed -n '1p' $task)
    load_file=$(sed -n '2p' $task)
    save_file=$(sed -n '3p' $task)
    save_link=$(sed -n '4p' $task)

    # Download from GCS (max 3 attempts)
    for i in {1..3}; do
        echo "Downloading $save_link to $load_file (Attempt $i of 3)"
        gcloud storage cp $load_link $load_file > /dev/null 2>&1 && break
        echo "Failed to download $load_link, retrying..." && sleep 5
        if [ $i -eq 3 ]; then
            echo "ERROR: Failed to download $load_link after 3 attempts." >&2
            return 1
        fi
    done

    # Transform the file (max 3 attempts)
    for i in {1..3}; do
        echo "Transforming $load_file (Attempt $i of 3)"
        mkdir -p $(dirname $save_file)
        CUDA_VISIBLE_DEVICES=$SLURM_PROCID python3 -m sources.textbook \
            --load-file $load_file --save-file $save_file --model $INSTRUCTOR && break
        echo "Failed to transform $load_file, retrying..." && sleep 5
        if [ $i -eq 3 ]; then
            echo "ERROR: Failed to transform $load_file after 3 attempts." >&2
            return 1
        fi
    done

    # Upload to GCS (max 3 attempts)
    for i in {1..3}; do
        echo "Uploading $save_file to $save_link (Attempt $i of 3)"
        gcloud storage cp $save_file $save_link > /dev/null 2>&1 && break
        echo "Failed to upload $save_file, retrying..." && sleep 5
        if [ $i -eq 3 ]; then
            echo "ERROR: Failed to upload $save_file after 3 attempts." >&2
            return 1
        fi
    done

    # Mark task as completed
    > $task
}

main() {
    source devconfig.sh
    source devsecret.sh
    export QUEUE=$NFS_MOUNT/queue/$DATASET-textbook/$INSTRUCTOR/

    export -f textbook
    find $QUEUE -type f -name "*.task" | sort | while read -r line; do
        flock -n $line -c "textbook $line" || true
    done
}

main

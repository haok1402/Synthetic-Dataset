#!/bin/bash

# Author: Hao Kang
# Date: May 29, 2025

#SBATCH --job-name=textbook
#SBATCH --output=logs/%x-%j.log
#SBATCH --time=2-00:00:00
#SBATCH --partition=preempt

main() {
    source devconfig.sh
    source devsecret.sh

    export QUEUE=$NFS_MOUNT/queue/$DATASET-textbook/$INSTRUCTOR/
    echo "Queue: $QUEUE"

    if [ -d $QUEUE ]; then
        find $QUEUE -type f -name "*.task" -empty -delete
    else
        mkdir -p $QUEUE
        gcloud storage ls $GCP_ENTRY/$DATASET/textfiles/ | while read -r load_link; do
            name=$(basename $load_link)
            load_file=$SSD_ENTRY/$DATASET/textfiles/$name
            save_file=$SSD_ENTRY/$DATASET-textbook/$INSTRUCTOR/$name
            save_link=$GCP_ENTRY/$DATASET-textbook/$INSTRUCTOR/$name
            task=$QUEUE/$name.task
            echo $load_link > $task
            echo $load_file >> $task
            echo $save_file >> $task
            echo $save_link >> $task
        done
    fi
}

main

#!/bin/bash
# Transform the corpus into academic, textbook style.

# Author: Hao Kang
# Date: May 22, 2025

#SBATCH --job-name=textbook
#SBATCH --output=logs/textbook-%A/task-%a.log
#SBATCH --array=0-49
#SBATCH --requeue

#SBATCH --mem=64GB
#SBATCH --cpus-per-task=32
#SBATCH --gres=gpu:1
#SBATCH --time=2-00:00:00

# Setup the environment.
source devconfig.sh
source devsecret.env

# Dispatch the task.
python3 -m sources.textbook \
    --task-id $SLURM_ARRAY_TASK_ID \
    --task-count $SLURM_ARRAY_TASK_COUNT \
    --load-from "$DATASET_DIR/dclm-28B/*.jsonl" \
    --save-into "$DATASET_DIR/dclm-28B-synthetic/academic" \
    --model mistralai/Mistral-7B-Instruct-v0.2

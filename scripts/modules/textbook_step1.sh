#!/bin/bash
# Transform the corpus into academic, textbook style.

# Author: Hao Kang
# Date: May 22, 2025

TASK_ID=$((SLURM_ARRAY_TASK_ID * SLURM_NPROCS + SLURM_PROCID))
TASK_COUNT=$((SLURM_ARRAY_TASK_COUNT * SLURM_NPROCS))

IFS=',' read -ra GPU_IDS <<< "$SLURM_JOB_GPUS"
export CUDA_VISIBLE_DEVICES=${GPU_IDS[$SLURM_PROCID]}

python3 -m sources.textbook \
    --task-id $TASK_ID --task-count $TASK_COUNT \
    --load-from "$DATASET_DIR/dclm-28B/*.jsonl" \
    --save-into "$DATASET_DIR/dclm-28B-synthetic/academic" \
    --model mistralai/Mistral-7B-Instruct-v0.2

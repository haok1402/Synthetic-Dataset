#!/bin/bash
# Set up the runtime environment.

export GCP_BUCKET=cmu-gpucloud-haok
export GCP_PREFIX=MoE-Research/dataset

if [[ $(hostname) == orchard-* ]]; then
    export HF_HOME=/mnt/localssd/huggingface
elif [[ $(hostname) == babel-* ]]; then
    export HF_HOME=/data/user_data/haok/huggingface
fi

source ~/miniconda3/etc/profile.d/conda.sh
conda activate synthetic-dataset

#!/bin/bash
# Set up the runtime environment.

export GCP_BUCKET=cmu-gpucloud-haok
export GCP_PREFIX=MoE-Research/dataset

source ~/miniconda3/etc/profile.d/conda.sh
conda activate synthetic-dataset

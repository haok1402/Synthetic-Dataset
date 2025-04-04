#!/bin/bash
# Set up the runtime environment.

export NFS_MOUNT=$PWD
export SSD_MOUNT=/mnt/localssd
export GCP_MOUNT=gs://cmu-gpucloud-haok

export SSD_ENTRY=$SSD_MOUNT/synthetic-dataset
export GCP_ENTRY=$GCP_MOUNT/MoE-Research/dataset

source ~/miniconda3/etc/profile.d/conda.sh
conda activate synthetic-dataset

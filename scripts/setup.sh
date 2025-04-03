#!/bin/bash

#SBATCH --job-name=setup
#SBATCH --output=logs/%x.log
#SBATCH --partition=preempt
#SBATCH --time=1:00:00

#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1

source ~/miniconda3/etc/profile.d/conda.sh
conda activate synthetic-dataset
pip install -r requirements.txt

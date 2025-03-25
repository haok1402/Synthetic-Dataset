#!/bin/bash
# Transform the corpus into academic, textbook style.

# Author: Hao Kang
# Date: May 22, 2025

#SBATCH --job-name=textbook
#SBATCH --output=logs/textbook-%A/task-%a.log

#SBATCH --array=0-49%16
#SBATCH --time=2-00:00:00
#SBATCH --requeue

#SBATCH --ntasks=2
#SBATCH --cpus-per-task=24
#SBATCH --gres=gpu:2
#SBATCH --mem-per-gpu=64GB

# Setup the environment.
source devconfig.sh
source devsecret.env

# Dispatch each task.
srun -W 0 scripts/modules/textbook_step1.sh

#!/bin/bash

# Author: Hao Kang
# Date: May 29, 2025

#SBATCH --job-name=textbook
#SBATCH --output=logs/textbook-%A/task-%a.log
#SBATCH --time=2-00:00:00
#SBATCH --partition=preempt

#SBATCH --ntasks=2
#SBATCH --array=0-31%8
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=24
#SBATCH --gres=gpu:2
#SBATCH --mem-per-gpu=64GB

srun -W 0 scripts/modules/textbook_job2_step1.sh

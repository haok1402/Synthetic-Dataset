#!/bin/bash

#SBATCH --job-name=textbook
#SBATCH --output=logs/%x/%A/task-%a.log
#SBATCH --time=2-00:00:00
#SBATCH --partition=general

#SBATCH --ntasks=2
#SBATCH --array=0-11
#SBATCH --cpus-per-task=24
#SBATCH --gres=gpu:A6000:2
#SBATCH --mem-per-gpu=64GB

source devconfig.sh
source devsecret.sh

srun -W 0 scripts/modules/textbook_job2_step1.sh

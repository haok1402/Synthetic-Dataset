#!/bin/bash

#SBATCH --job-name=textbook
#SBATCH --output=logs/%x/%A-%a.log
#SBATCH --time=2-00:00:00
#SBATCH --partition=preempt

#SBATCH --ntasks=2
#SBATCH --array=0-31
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=24
#SBATCH --gres=gpu:2
#SBATCH --mem-per-gpu=64GB

source devconfig.sh
source devsecret.sh

python3 -m sources.textbook.dispatch

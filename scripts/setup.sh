#!/bin/bash
# Setup the conda environment.

SCRIPT=scripts/modules/setup_job1.sh

if [[ $(hostname) == orchard-* ]]; then
    sbatch $SCRIPT
elif [[ $(hostname) == babel-* ]]; then
    sbatch --partition=general --gres=gpu:A6000:1 $SCRIPT
fi

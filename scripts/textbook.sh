#!/bin/bash
# Dispatch the textbook synthesis.

SCRIPT=scripts/modules/textbook_job2.sh

if [[ $(hostname) == orchard-* ]]; then
    sbatch $SCRIPT
elif [[ $(hostname) == babel-* ]]; then
    sbatch --partition=general --gres=gpu:A6000:2 --array=0-11 $SCRIPT
fi

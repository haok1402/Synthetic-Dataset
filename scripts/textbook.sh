#!/bin/bash
# Dispatch the textbook synthesis.

if [[ $(hostname) == orchard-* ]]; then
    sbatch scripts/modules/flame_textbook_job2.sh
elif [[ $(hostname) == babel-* ]]; then
    sbatch scripts/modules/babel_textbook_job2.sh
fi

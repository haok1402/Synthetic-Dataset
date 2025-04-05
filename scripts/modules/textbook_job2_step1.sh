#!/bin/bash

source devconfig.sh
source devsecret.sh

CUDA_VISIBLE_DEVICES=$SLURM_PROCID python3 -m sources.textbook.dispatch

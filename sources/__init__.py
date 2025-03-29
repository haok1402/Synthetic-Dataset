"""
Initialize the pipeline for synthetic dataset.

Author: Hao Kang
Date: March 22, 2025
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--load-file", type=str, required=True)
parser.add_argument("--save-file", type=str, required=True)
parser.add_argument("--model", type=str, required=True)
parsed = parser.parse_args()

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

import tenacity
from vllm import LLM

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
    retry=tenacity.retry_if_exception_type(Exception),
    reraise=True
)
def load_engine():
    """
    Loads the model using the vLLM library. Note that this process makes requests to Hugging Face's servers.
    When running distributed jobs with SLURM, multiple requests may be made simultaneously during the start time,
    which could sometimes lead to rate-limiting or other issues. That's why the retry logic was added.
    """
    return LLM(parsed.model)

engine = load_engine()

"""
Author: Hao Kang
Date: March 22, 2025
"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--task-id", type=int, default=0)
parser.add_argument("--task-count", type=int, default=1)
parser.add_argument("--load-from", type=str, required=True)
parser.add_argument("--save-into", type=str, required=True)
parser.add_argument("--model", type=str, required=True)
parsed = parser.parse_args()

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")

from vllm import LLM

llm = LLM(parsed.model)

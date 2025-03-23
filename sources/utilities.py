"""
Author: Hao Kang
Date: March 23, 2025
"""

import hashlib
from pathlib import Path


def hash_file(path: Path) -> str:
    algo = hashlib.new("sha256")
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            algo.update(chunk)
    return algo.hexdigest()

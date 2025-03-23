"""
Transform the corpus into academic, textbook style.

Author: Zichun Yu, Hao Kang
Date: March 22, 2025
"""

import os
import glob
import json
import logging
from typing import List
from pathlib import Path
from vllm import SamplingParams
from sources import parsed, engine


sampling_params = SamplingParams(
    repetition_penalty=1.2,
    temperature=0.6,
    top_p=0.95, top_k=50,
    max_tokens=2500,
)


prompt_template = \
"""Here is an extract from a webpage: "{text}".

Write an extensive and detailed course unit suitable for a textbook targeted at college students, related to the given extract. Do not just list concepts, but develop each one in detail before moving to the next, as we prioritize depth of understanding and comprehensive exploration of the subject matter over breadth. Focus on:

- Rigor: Ensure in-depth coverage of the concepts/sections.
- Engagement: Write with an academic, professional and engaging tone that captivates interest.
- Application: Incorporate specific, practical examples, such as proofs in calculus or critical dates and figures in history.
Do not include a title or an introduction, simply write the content without headlines and introductory phrases. Do not use images."""


def transform(corpus: List[str]) -> List[str]:
    prompts = [prompt_template.format(text=text) for text in corpus]
    outputs = engine.generate(prompts, sampling_params)
    return [item.outputs[0].text for item in outputs]


def main():
    store = Path(parsed.save_into)
    store.mkdir(mode=0o770, parents=True, exist_ok=True)
    files = sorted(filter(os.path.isfile, glob.glob(parsed.load_from)))
    files = [Path(path) for path in files]

    for i, path in enumerate(files):
        if path.suffix != ".jsonl":
            raise NotImplementedError("Only 'jsonl' files are allowed.")
        if i % parsed.task_count != parsed.task_id:
            continue

        corpus = list()
        logging.info(f"Reading the corpus from {path}.")
        with path.open("r") as fp:
            for line in fp:
                data = json.loads(line)
                text = prompt_template.format(text=data["text"])
                corpus.append(text)

        logging.info("Transforming the corpus into academic, textbook style.")
        corpus = transform(corpus)

        path = Path(store, path.name)
        logging.info(f"Saving the corpus into {path}.")
        with path.open("w") as fp:
            for text in corpus:
                line = json.dumps({"text": text})
                fp.write(data + "\n")


if __name__ == '__main__':
    main()

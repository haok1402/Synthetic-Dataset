import json
import time
from typing import List
from tqdm import tqdm
from vllm import LLM, TokensPrompt, SamplingParams
from sources.textbook import store, queue

sampling_params = SamplingParams(
    repetition_penalty=1.2,
    temperature=0.6,
    top_p=0.95, top_k=50,
    max_tokens=2048,
)

prompt_template = """
Here is an extract from a webpage: "{text}".

Write an extensive and detailed course unit suitable for a textbook targeted at college students, related to the given extract. Do not just list concepts, but develop each one in detail before moving to the next, as we prioritize depth of understanding and comprehensive exploration of the subject matter over breadth. Focus on:

- Rigor: Ensure in-depth coverage of the concepts/sections.
- Engagement: Write with an academic, professional and engaging tone that captivates interest.
- Application: Incorporate specific, practical examples, such as proofs in calculus or critical dates and figures in history.

Do not include a title or an introduction, simply write the content without headlines and introductory phrases. Do not use images.
"""

def transform(tid: str, engine: LLM, batch: List[str]) -> List[str]:
    # Generate the text using the LLM engine
    prompts = [prompt_template.format(text=text) for text in batch]
    max_length = engine.llm_engine.model_config.max_model_len - sampling_params.max_tokens
    t0 = time.time()
    encoded = engine.get_tokenizer().batch_encode_plus(prompts, truncation=True, max_length=max_length)
    encoded = list(map(lambda x: TokensPrompt(prompt_token_ids=x), encoded['input_ids']))
    outputs = engine.generate(encoded, sampling_params, use_tqdm=False)
    t1 = time.time()
    # Calculate and report throughput metrics
    itps = sum([len(x.prompt_token_ids) for x in outputs]) / (t1 - t0)
    otps = sum([len(x.outputs[0].token_ids) for x in outputs]) / (t1 - t0)
    queue.update(tid, {"itps": itps, "otps": otps})
    return [item.outputs[0].text for item in outputs]

def main():
    while task := queue.acquire():
        tid, params = task
        engine = LLM(model=params["model"], task="generate")
        # Read the corpus from the specified blob
        corpus = []
        with store.blob(params["read-from"]).open("r") as fp:
            for line in fp:
                data = json.loads(line.strip())
                corpus.append(data["text"])
        # Process the corpus in batches and save the results
        batch_size = 64
        with store.blob(params["save-into"]).open("w") as fp2:
            for i in tqdm(range(0, len(corpus), batch_size), mininterval=8):
                batch = corpus[i:i + batch_size]
                for text in transform(tid, engine, batch):
                    fp2.write(json.dumps({"text": text}) + "\n")
        queue.release(tid)

if __name__ == "__main__":
    main()

# Textbook

This pipeline transforms a corpus into an academic, textbook-style format, generating synthetic datasets for pre-training large language models. Below are examples on how to configure and execute the pipeline.

## DCLM-28B

**Mistral-7B-Instruct-v0.2:**

```bash
export DATASET=dclm28b
export INSTRUCTOR=mistralai/Mistral-7B-Instruct-v0.2
sbatch scripts/modules/textbook_job1.sh
```

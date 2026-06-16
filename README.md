# UROP---project-Detect-hallucinations-in-LLMs-
Detecting and Explaining Hallucinations in Large Language Models

This repository now includes a small dependency-free claim support classifier for RAG-style answers.

## What it does

`claim_support.py` splits an AI response into individual claims and compares each claim with retrieved source documents. Every claim is classified as:

- `supported`
- `partially_supported`
- `unsupported`

The output also includes the strongest matching evidence snippet and a confidence-style score.

## Example

```bash
python claim_support.py \
  --response "Paris is the capital of France. Berlin is the capital of France." \
  --source "Paris is the capital of France."
```

## Tests

```bash
python -m unittest tests/test_claim_support.py -v
```

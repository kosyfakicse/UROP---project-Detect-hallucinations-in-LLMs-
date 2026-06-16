from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from typing import Iterable, List, Sequence


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "to",
    "was",
    "were",
    "will",
    "with",
}


@dataclass(frozen=True)
class ClaimAssessment:
    claim: str
    classification: str
    evidence: str
    score: float


def split_claims(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip(" -•\t") for part in parts if part.strip(" -•\t")]


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def _content_tokens(text: str) -> List[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text))


def _anchor_tokens(text: str) -> set[str]:
    anchors = set()
    for token in re.findall(r"\b[A-Za-z0-9]+\b", text):
        if token.isdigit():
            anchors.add(token)
        elif len(token) > 1 and token[0].isupper():
            anchors.add(token.lower())
    return anchors


def _bigrams(tokens: Sequence[str]) -> set[tuple[str, str]]:
    return set(zip(tokens, tokens[1:]))


def _iter_candidates(source_documents: Iterable[str]) -> Iterable[str]:
    for document in source_documents:
        cleaned = document.strip()
        if not cleaned:
            continue
        yield cleaned
        for sentence in split_claims(cleaned):
            if sentence != cleaned:
                yield sentence


def _assess_against_source(claim: str, source: str) -> tuple[float, str]:
    normalized_claim = _normalize(claim)
    normalized_source = _normalize(source)

    if normalized_claim and normalized_claim in normalized_source:
        return 1.0, "supported"

    claim_tokens = _content_tokens(claim)
    source_token_list = _content_tokens(source)
    source_tokens = set(source_token_list)
    if not claim_tokens:
        return 0.0, "unsupported"

    matched_tokens = [token for token in claim_tokens if token in source_tokens]
    token_coverage = len(matched_tokens) / len(claim_tokens)

    claim_bigrams = _bigrams(claim_tokens)
    source_bigrams = _bigrams(source_token_list)
    if claim_bigrams:
        bigram_overlap = len(claim_bigrams & source_bigrams) / len(claim_bigrams)
    else:
        bigram_overlap = 1.0 if token_coverage else 0.0

    claim_numbers = _numbers(claim)
    source_numbers = _numbers(source)
    numbers_match = not claim_numbers or claim_numbers <= source_numbers
    claim_anchors = _anchor_tokens(claim)
    source_anchors = _anchor_tokens(source)
    anchor_match = not claim_anchors or claim_anchors <= source_anchors

    score = round(
        token_coverage * 0.75
        + bigram_overlap * 0.15
        + (0.05 if numbers_match else -0.1)
        + (0.05 if anchor_match else -0.15),
        3,
    )

    if token_coverage >= 0.85 and numbers_match and anchor_match:
        return score, "supported"
    if anchor_match and token_coverage >= 0.45 and (bigram_overlap > 0 or len(matched_tokens) >= 2):
        return score, "partially_supported"
    return score, "unsupported"


def classify_claim(claim: str, source_documents: Sequence[str]) -> ClaimAssessment:
    best_score = float("-inf")
    best_label = "unsupported"
    best_evidence = ""

    for candidate in _iter_candidates(source_documents):
        score, label = _assess_against_source(claim, candidate)
        if score > best_score:
            best_score = score
            best_label = label
            best_evidence = candidate

    if best_score == float("-inf"):
        best_score = 0.0

    return ClaimAssessment(
        claim=claim,
        classification=best_label,
        evidence=best_evidence,
        score=round(max(best_score, 0.0), 3),
    )


def classify_response_claims(response: str, source_documents: Sequence[str]) -> List[ClaimAssessment]:
    return [classify_claim(claim, source_documents) for claim in split_claims(response)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify response claims against retrieved source documents.")
    parser.add_argument("--response", required=True, help="AI-generated response to analyze.")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        dest="sources",
        help="Retrieved source document. Pass once per source.",
    )
    args = parser.parse_args()

    assessments = classify_response_claims(args.response, args.sources)
    print(json.dumps([asdict(assessment) for assessment in assessments], indent=2))


if __name__ == "__main__":
    main()

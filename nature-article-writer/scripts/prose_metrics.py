\
#!/usr/bin/env python3
"""
Utility functions for lightweight manuscript-style diagnostics.

This module is stdlib-only and is intended for non-interactive use by
scripts/prose_fingerprint.py and scripts/nature_preflight.py.
"""

from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

WORDS_RE = re.compile(r"\b[\w'-]+\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
PARA_SPLIT_RE = re.compile(r"\n\s*\n", re.M)
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9-]{1,}\b")
BE_VERB_RE = re.compile(r"\b(?:am|is|are|was|were|be|been|being)\b", re.I)
PAST_PARTICIPLE_RE = re.compile(r"\b\w+(?:ed|en)\b", re.I)
NOMINALIZATION_RE = re.compile(r"\b\w+(?:tion|sion|ment|ance|ence|ity|ness)\b", re.I)

TRANSITION_OPENERS = {
    "additionally", "moreover", "furthermore", "importantly", "notably", "overall",
    "therefore", "however", "thus", "consequently", "meanwhile", "taken", "together",
    "in summary", "in conclusion"
}

WEAK_OPENERS = {"this", "these", "it", "we", "here"}

HYPE_WORDS = {
    "novel", "groundbreaking", "transformative", "remarkable", "unprecedented",
    "critical", "crucial", "important", "compelling", "robust", "exciting"
}

GENERIC_PHRASES = [
    "highlights the importance of",
    "underscores the importance of",
    "plays a crucial role",
    "taken together",
    "in the broader context",
    "opens new avenues",
    "paves the way",
    "it is important to note that",
    "provides valuable insights",
    "state-of-the-art",
    "not only",
    "not merely",
    "in this landscape",
    "interplay",
    "leverages",
    "fosters",
]

HEDGE_WORDS = {
    "may", "might", "could", "suggest", "suggests", "suggested", "appear", "appears",
    "likely", "possibly", "consistent", "indicate", "indicates", "associated"
}


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            return parts[1]
    return text


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def paragraphs(text: str) -> List[str]:
    return [p.strip() for p in PARA_SPLIT_RE.split(strip_frontmatter(text)) if p.strip()]


def sentences(text: str) -> List[str]:
    clean = strip_frontmatter(text).strip()
    if not clean:
        return []
    raw = [s.strip() for s in SENTENCE_SPLIT_RE.split(clean) if s.strip()]
    return raw


def words(text: str) -> List[str]:
    return WORDS_RE.findall(text)


def ratio(count: int, total: int) -> float:
    return 0.0 if total <= 0 else count / total


def safe_mean(xs: Sequence[float]) -> float:
    return float(statistics.mean(xs)) if xs else 0.0


def safe_median(xs: Sequence[float]) -> float:
    return float(statistics.median(xs)) if xs else 0.0


def safe_stdev(xs: Sequence[float]) -> float:
    if len(xs) <= 1:
        return 0.0
    return float(statistics.pstdev(xs))


def sentence_lengths(sents: Sequence[str]) -> List[int]:
    return [len(words(s)) for s in sents if words(s)]


def paragraph_lengths(paras: Sequence[str]) -> List[int]:
    return [len(words(p)) for p in paras if words(p)]


def first_word(sentence: str) -> str:
    toks = words(sentence.lower())
    return toks[0] if toks else ""


def first_two_words(sentence: str) -> str:
    toks = words(sentence.lower())
    return " ".join(toks[:2]) if toks else ""


def transition_opener_count(sents: Sequence[str]) -> int:
    count = 0
    for s in sents:
        opener = first_two_words(s)
        opener1 = first_word(s)
        if opener in TRANSITION_OPENERS or opener1 in TRANSITION_OPENERS:
            count += 1
    return count


def weak_opener_count(sents: Sequence[str]) -> int:
    return sum(1 for s in sents if first_word(s) in WEAK_OPENERS)


def repeated_openers(sents: Sequence[str], n: int = 5) -> Dict[str, int]:
    c = Counter(first_word(s) for s in sents if first_word(s))
    return dict(c.most_common(n))


def repeated_bigrams(sents: Sequence[str], n: int = 5) -> Dict[str, int]:
    c = Counter(first_two_words(s) for s in sents if first_two_words(s))
    return dict(c.most_common(n))


def passive_cues(sents: Sequence[str]) -> int:
    count = 0
    for s in sents:
        if BE_VERB_RE.search(s) and PAST_PARTICIPLE_RE.search(s):
            count += 1
    return count


def participial_clause_cues(sents: Sequence[str]) -> int:
    count = 0
    pattern = re.compile(r"(?:^|,\s+)\w+(?:ing)\b", re.I)
    for s in sents:
        if pattern.search(s):
            count += 1
    return count


def nominalizations(tokens: Sequence[str]) -> int:
    return sum(1 for t in tokens if NOMINALIZATION_RE.fullmatch(t))


def acronym_count(tokens: Sequence[str]) -> int:
    return sum(1 for t in tokens if ACRONYM_RE.fullmatch(t))


def phrase_hits(text: str, phrases: Sequence[str]) -> Dict[str, int]:
    lower = text.lower()
    hits: Dict[str, int] = {}
    for phrase in phrases:
        n = lower.count(phrase.lower())
        if n:
            hits[phrase] = n
    return hits


def word_hits(tokens: Sequence[str], vocab: Iterable[str]) -> Dict[str, int]:
    vocab_set = {v.lower() for v in vocab}
    c = Counter(t.lower() for t in tokens)
    return {w: c[w] for w in sorted(vocab_set) if c[w]}


def endings(text: str) -> List[str]:
    sents = sentences(text)
    enders = []
    for s in sents:
        toks = words(s.lower())
        if toks:
            enders.append(toks[-1])
    return enders


def flatness_score(lengths: Sequence[int]) -> float:
    """
    Low variance in sentence lengths is one proxy for rhythm flatness.
    Returns a score in [0, 1], where higher means flatter.
    """
    if len(lengths) < 3:
        return 0.0
    mean = safe_mean(lengths)
    stdev = safe_stdev(lengths)
    if mean <= 0:
        return 0.0
    cv = stdev / mean
    score = max(0.0, min(1.0, 0.5 - cv))
    return round(score, 3)


def metrics(text: str) -> Dict[str, Any]:
    clean = strip_frontmatter(text)
    sents = sentences(clean)
    paras = paragraphs(clean)
    toks = words(clean)

    slens = sentence_lengths(sents)
    plens = paragraph_lengths(paras)

    hype = word_hits(toks, HYPE_WORDS)
    generic = phrase_hits(clean, GENERIC_PHRASES)
    hedge = word_hits(toks, HEDGE_WORDS)

    m: Dict[str, Any] = {
        "word_count": len(toks),
        "sentence_count": len(sents),
        "paragraph_count": len(paras),
        "mean_sentence_words": round(safe_mean(slens), 2),
        "median_sentence_words": round(safe_median(slens), 2),
        "stdev_sentence_words": round(safe_stdev(slens), 2),
        "mean_paragraph_words": round(safe_mean(plens), 2),
        "median_paragraph_words": round(safe_median(plens), 2),
        "stdev_paragraph_words": round(safe_stdev(plens), 2),
        "flatness_score": flatness_score(slens),
        "acronym_count": acronym_count(toks),
        "acronym_rate": round(ratio(acronym_count(toks), len(toks)), 4),
        "nominalization_count": nominalizations(toks),
        "nominalization_rate": round(ratio(nominalizations(toks), len(toks)), 4),
        "participial_clause_cues": participial_clause_cues(sents),
        "participial_clause_rate": round(ratio(participial_clause_cues(sents), len(sents)), 4),
        "passive_cue_sentences": passive_cues(sents),
        "passive_cue_rate": round(ratio(passive_cues(sents), len(sents)), 4),
        "transition_opener_count": transition_opener_count(sents),
        "transition_opener_rate": round(ratio(transition_opener_count(sents), len(sents)), 4),
        "weak_opener_count": weak_opener_count(sents),
        "weak_opener_rate": round(ratio(weak_opener_count(sents), len(sents)), 4),
        "hype_words": hype,
        "hype_word_total": sum(hype.values()),
        "generic_phrases": generic,
        "generic_phrase_total": sum(generic.values()),
        "hedge_words": hedge,
        "hedge_word_total": sum(hedge.values()),
        "top_sentence_openers": repeated_openers(sents, n=8),
        "top_sentence_opener_bigrams": repeated_bigrams(sents, n=8),
        "ending_words_top": dict(Counter(endings(clean)).most_common(8)),
    }
    return m


def aggregate(metrics_list: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not metrics_list:
        return {}
    numeric_keys = [
        "word_count", "sentence_count", "paragraph_count",
        "mean_sentence_words", "median_sentence_words", "stdev_sentence_words",
        "mean_paragraph_words", "median_paragraph_words", "stdev_paragraph_words",
        "flatness_score",
        "acronym_count", "acronym_rate",
        "nominalization_count", "nominalization_rate",
        "participial_clause_cues", "participial_clause_rate",
        "passive_cue_sentences", "passive_cue_rate",
        "transition_opener_count", "transition_opener_rate",
        "weak_opener_count", "weak_opener_rate",
        "hype_word_total", "generic_phrase_total", "hedge_word_total",
    ]
    out: Dict[str, Any] = {}
    for key in numeric_keys:
        values = [float(m.get(key, 0.0)) for m in metrics_list]
        out[key] = round(safe_mean(values), 4)
    # Merge counters by summed counts
    counter_keys = ["top_sentence_openers", "top_sentence_opener_bigrams", "ending_words_top", "hype_words", "generic_phrases", "hedge_words"]
    for key in counter_keys:
        merged = Counter()
        for m in metrics_list:
            merged.update(m.get(key, {}))
        out[key] = dict(merged.most_common(10))
    out["reference_count"] = len(metrics_list)
    return out


def compare(candidate: Dict[str, Any], reference: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compare candidate metrics against aggregated reference metrics.
    Returns a list of deltas with suggested interpretation.
    """
    fields = [
        ("mean_sentence_words", "sentence length"),
        ("stdev_sentence_words", "sentence-length variation"),
        ("mean_paragraph_words", "paragraph length"),
        ("nominalization_rate", "nominalization rate"),
        ("participial_clause_rate", "participial-clause rate"),
        ("transition_opener_rate", "transition-opener rate"),
        ("weak_opener_rate", "weak-opener rate"),
        ("acronym_rate", "acronym rate"),
        ("flatness_score", "rhythm flatness score"),
        ("passive_cue_rate", "passive-cue rate"),
        ("hedge_word_total", "hedge-word density"),
        ("hype_word_total", "hype-word density"),
        ("generic_phrase_total", "generic-phrase density"),
    ]
    results = []
    sentence_count = max(1, int(candidate.get("sentence_count", 1)))
    ref_sentence_count = max(1, int(reference.get("sentence_count", sentence_count)))
    cand_word_count = max(1, int(candidate.get("word_count", 1)))
    ref_word_count = max(1, int(reference.get("word_count", cand_word_count)))

    for key, label in fields:
        cand = float(candidate.get(key, 0.0))
        ref = float(reference.get(key, 0.0))
        # Normalise totals to rates when totals are used.
        if key in {"hedge_word_total", "hype_word_total", "generic_phrase_total"}:
            cand = cand / cand_word_count
            ref = ref / ref_word_count
        delta = cand - ref
        results.append({
            "metric": key,
            "label": label,
            "candidate": round(cand, 4),
            "reference": round(ref, 4),
            "delta": round(delta, 4),
        })
    return results


def rank_revision_priorities(comparisons: Sequence[Dict[str, Any]]) -> List[str]:
    priorities: List[str] = []
    for item in sorted(comparisons, key=lambda x: abs(x["delta"]), reverse=True):
        label = item["label"]
        d = item["delta"]
        if label == "nominalization rate" and d > 0.01:
            priorities.append("Reduce noun-heavy nominalizations; turn hidden verbs back into actions where possible.")
        elif label == "participial-clause rate" and d > 0.05:
            priorities.append("Break long '-ing' clause chains into clearer main clauses and shorter sentences.")
        elif label == "transition-opener rate" and d > 0.03:
            priorities.append("Cut conveyor-belt transitions and let structure carry more of the logic.")
        elif label == "weak-opener rate" and d > 0.05:
            priorities.append("Vary sentence openings; too many sentences start with weak pronouns or generic 'we' statements.")
        elif label == "sentence-length variation" and d < -2:
            priorities.append("Sentence rhythm is flatter than the references; vary sentence length more deliberately.")
        elif label == "sentence length" and d > 4:
            priorities.append("Average sentences are much longer than the references; split overloaded sentences.")
        elif label == "acronym rate" and d > 0.01:
            priorities.append("Acronym density is high relative to the reference set; unpack or remove non-essential abbreviations.")
        elif label == "hype-word density" and d > 0:
            priorities.append("Cut adjective-led importance language and let the evidence carry the emphasis.")
        elif label == "generic-phrase density" and d > 0:
            priorities.append("Replace generic manuscript phrases with precise claims or implications.")
        elif label == "rhythm flatness score" and d > 0.1:
            priorities.append("Sentence rhythm is unusually flat; mix short claim sentences with longer explanatory ones.")
    seen = set()
    unique = []
    for p in priorities:
        if p not in seen:
            unique.append(p)
            seen.add(p)
    return unique[:8]


def as_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


__all__ = [
    "read_text",
    "strip_frontmatter",
    "paragraphs",
    "sentences",
    "words",
    "metrics",
    "aggregate",
    "compare",
    "rank_revision_priorities",
    "as_json",
]

\
#!/usr/bin/env python3
"""
Compare a candidate manuscript against one or more reference texts and report
stylistic alignment cues. This is intended to help an agent match broad habits
of sentence movement and paragraph density without copying phrasing.

Examples:
  python3 scripts/prose_fingerprint.py --candidate draft.md --reference paper1.md paper2.md
  python3 scripts/prose_fingerprint.py --input draft.md exemplar.md --format json

Exit codes:
  0  success
  2  usage error or unreadable file
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from prose_metrics import (
    aggregate,
    as_json,
    compare,
    metrics,
    rank_revision_priorities,
    read_text,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compare a candidate manuscript against reference texts and report high-level prose alignment cues."
    )
    p.add_argument(
        "--candidate",
        help="Candidate draft to analyse."
    )
    p.add_argument(
        "--reference",
        nargs="+",
        help="One or more reference texts to compare against."
    )
    p.add_argument(
        "--input",
        nargs="+",
        help="Alternative interface: pass multiple files, with the first treated as candidate and the rest as references."
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format."
    )
    return p


def resolve_args(args: argparse.Namespace) -> tuple[str, List[str]]:
    if args.input:
        if len(args.input) < 2:
            raise SystemExit("Error: --input requires at least two files: candidate followed by one or more references.")
        return args.input[0], args.input[1:]
    if not args.candidate or not args.reference:
        raise SystemExit("Error: provide either --candidate with --reference, or use --input.")
    return args.candidate, list(args.reference)


def load(path: str) -> str:
    try:
        return read_text(path)
    except FileNotFoundError:
        raise SystemExit(f"Error: file not found: {path}")
    except OSError as exc:
        raise SystemExit(f"Error: could not read {path}: {exc}")


def text_report(candidate_path: str, candidate_metrics: dict, reference_paths: List[str], reference_metrics: dict, deltas: list, priorities: list) -> str:
    lines = []
    lines.append("Prose fingerprint report")
    lines.append("======================")
    lines.append(f"Candidate: {candidate_path}")
    lines.append(f"References ({len(reference_paths)}): " + ", ".join(reference_paths))
    lines.append("")
    lines.append("Candidate profile")
    lines.append("-----------------")
    lines.append(f"- words: {candidate_metrics['word_count']}")
    lines.append(f"- sentences: {candidate_metrics['sentence_count']}")
    lines.append(f"- mean sentence length: {candidate_metrics['mean_sentence_words']} words")
    lines.append(f"- sentence-length variation: {candidate_metrics['stdev_sentence_words']}")
    lines.append(f"- mean paragraph length: {candidate_metrics['mean_paragraph_words']} words")
    lines.append(f"- nominalization rate: {candidate_metrics['nominalization_rate']}")
    lines.append(f"- participial-clause rate: {candidate_metrics['participial_clause_rate']}")
    lines.append(f"- transition-opener rate: {candidate_metrics['transition_opener_rate']}")
    lines.append(f"- weak-opener rate: {candidate_metrics['weak_opener_rate']}")
    lines.append(f"- acronym rate: {candidate_metrics['acronym_rate']}")
    lines.append(f"- rhythm flatness score: {candidate_metrics['flatness_score']}")
    lines.append("")
    lines.append("Reference aggregate")
    lines.append("-------------------")
    lines.append(f"- reference count: {reference_metrics.get('reference_count', len(reference_paths))}")
    lines.append(f"- mean sentence length: {reference_metrics['mean_sentence_words']} words")
    lines.append(f"- sentence-length variation: {reference_metrics['stdev_sentence_words']}")
    lines.append(f"- mean paragraph length: {reference_metrics['mean_paragraph_words']} words")
    lines.append(f"- nominalization rate: {reference_metrics['nominalization_rate']}")
    lines.append(f"- participial-clause rate: {reference_metrics['participial_clause_rate']}")
    lines.append(f"- transition-opener rate: {reference_metrics['transition_opener_rate']}")
    lines.append(f"- weak-opener rate: {reference_metrics['weak_opener_rate']}")
    lines.append(f"- acronym rate: {reference_metrics['acronym_rate']}")
    lines.append(f"- rhythm flatness score: {reference_metrics['flatness_score']}")
    lines.append("")
    lines.append("Largest divergences")
    lines.append("------------------")
    for item in sorted(deltas, key=lambda x: abs(x["delta"]), reverse=True)[:8]:
        if abs(item["delta"]) < 1e-9:
            direction = "matches"
            lines.append(f"- {item['label']}: candidate {direction} the references ({item['candidate']} vs {item['reference']})")
        else:
            direction = "higher" if item["delta"] > 0 else "lower"
            lines.append(f"- {item['label']}: candidate {direction} than references ({item['candidate']} vs {item['reference']})")
    lines.append("")
    lines.append("Frequent candidate openers")
    lines.append("--------------------------")
    for k, v in candidate_metrics["top_sentence_openers"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    if candidate_metrics["generic_phrases"]:
        lines.append("Generic phrases detected")
        lines.append("------------------------")
        for k, v in candidate_metrics["generic_phrases"].items():
            lines.append(f"- {k}: {v}")
        lines.append("")
    if candidate_metrics["hype_words"]:
        lines.append("Hype / evaluative words detected")
        lines.append("-------------------------------")
        for k, v in candidate_metrics["hype_words"].items():
            lines.append(f"- {k}: {v}")
        lines.append("")
    lines.append("Revision priorities")
    lines.append("-------------------")
    if priorities:
        for p in priorities:
            lines.append(f"- {p}")
    else:
        lines.append("- Candidate broadly aligns with the reference set on the measured dimensions. Review paragraph jobs manually for finer stylistic fit.")
    return "\n".join(lines)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    candidate_path, reference_paths = resolve_args(args)

    candidate_text = load(candidate_path)
    reference_texts = [load(p) for p in reference_paths]

    cand = metrics(candidate_text)
    refs = [metrics(t) for t in reference_texts]
    ref_agg = aggregate(refs)
    deltas = compare(cand, ref_agg)
    priorities = rank_revision_priorities(deltas)

    payload = {
        "candidate_path": candidate_path,
        "reference_paths": reference_paths,
        "candidate_metrics": cand,
        "reference_metrics": ref_agg,
        "comparisons": deltas,
        "revision_priorities": priorities,
    }

    if args.format == "json":
        print(as_json(payload))
    else:
        print(text_report(candidate_path, cand, reference_paths, ref_agg, deltas, priorities))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

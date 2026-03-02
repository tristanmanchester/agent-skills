\
#!/usr/bin/env python3
"""
Audit raw idea sets for near-duplicates and dominant patterns.

Accepted input:
- JSON list of strings
- JSON list of objects with name and concept or description
- Plain text with one idea per line
- Markdown bullets

Usage:
  python scripts/diversity_audit.py ideas.json
  python scripts/diversity_audit.py ideas.txt
  cat ideas.txt | python scripts/diversity_audit.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, List


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "how",
    "if", "in", "into", "is", "it", "its", "of", "on", "or", "our", "that", "the",
    "their", "there", "this", "to", "using", "with", "we", "you", "your", "than",
    "then", "will", "can", "could", "should", "would", "make", "help", "idea",
    "ideas", "new", "better"
}

TAG_PATTERNS = {
    "ai_or_agent": [r"\bai\b", r"\bagent\b", r"\bassistant\b", r"\bchatbot\b", r"\bllm\b"],
    "dashboard": [r"\bdashboard\b", r"\banalytics\b", r"\breport\b", r"\bmonitoring\b"],
    "marketplace": [r"\bmarketplace\b", r"\bplatform\b", r"\bnetwork\b"],
    "community": [r"\bcommunity\b", r"\bforum\b", r"\bmember\b"],
    "gamification": [r"\bgamif", r"\bpoints\b", r"\bbadge\b", r"\bleaderboard\b"],
    "personalisation": [r"\bpersonali", r"\brecommend", r"\bcustomi", r"\btailor"],
    "automation": [r"\bautomation\b", r"\bautomate\b", r"\bworkflow\b", r"\borchestrat"],
    "trust": [r"\bguarantee\b", r"\bproof\b", r"\baud(it|it trail)\b", r"\bescrow\b", r"\breversible\b"],
    "service": [r"\bconcierge\b", r"\bservice\b", r"\bmanual\b", r"\bhuman\b"],
    "business_model": [r"\bsubscription\b", r"\bpricing\b", r"\boutcome\b", r"\bpay\b"],
}

VALUE_PATTERNS = {
    "time": [r"\bfaster\b", r"\bsave time\b", r"\bminutes\b", r"\bworkflow\b"],
    "risk": [r"\brisk\b", r"\bcompliance\b", r"\btrust\b", r"\bsafe\b", r"\bguarantee\b"],
    "money": [r"\bcost\b", r"\brevenue\b", r"\bprice\b", r"\bpay\b"],
    "status": [r"\bstatus\b", r"\breputation\b", r"\bprestige\b"],
    "access": [r"\baccess\b", r"\bavailability\b", r"\bdistribution\b", r"\bchannel\b"],
    "delight": [r"\bdelight\b", r"\bfun\b", r"\bjoy\b", r"\bmagic\b"],
}

CHANNEL_PATTERNS = {
    "embedded": [r"\bintegration\b", r"\bplugin\b", r"\bembedded\b", r"\bin app\b"],
    "partner": [r"\bpartner\b", r"\bchannel\b", r"\breseller\b"],
    "content_or_referral": [r"\bshare\b", r"\breferral\b", r"\bcontent\b", r"\bviral\b"],
    "sales_led": [r"\bprocurement\b", r"\benterprise\b", r"\bsales\b"],
    "self_serve": [r"\bself serve\b", r"\bsign up\b", r"\bfree trial\b", r"\bwaitlist\b"],
}


@dataclass
class Idea:
    idx: int
    name: str
    text: str

    @property
    def combined(self) -> str:
        return f"{self.name}. {self.text}".strip(". ")


def load_text_from_path_or_stdin(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    if sys.stdin.isatty():
        raise SystemExit("Provide a file path or pipe input on stdin.")
    return sys.stdin.read()


def parse_ideas(raw: str) -> List[Idea]:
    stripped = raw.strip()
    if not stripped:
        raise SystemExit("No input ideas found.")

    # Try JSON first.
    try:
        data = json.loads(stripped)
        if isinstance(data, list):
            ideas: List[Idea] = []
            for i, item in enumerate(data, start=1):
                if isinstance(item, str):
                    ideas.append(Idea(i, f"Idea {i}", item.strip()))
                elif isinstance(item, dict):
                    name = str(item.get("name") or item.get("title") or f"Idea {i}").strip()
                    text = str(
                        item.get("concept")
                        or item.get("description")
                        or item.get("idea")
                        or item.get("summary")
                        or ""
                    ).strip()
                    if not text:
                        text = json.dumps(item, ensure_ascii=False)
                    ideas.append(Idea(i, name, text))
                else:
                    ideas.append(Idea(i, f"Idea {i}", str(item).strip()))
            return [idea for idea in ideas if idea.text]
    except json.JSONDecodeError:
        pass

    lines = []
    for line in stripped.splitlines():
        cleaned = re.sub(r"^\s*[-*+]\s+", "", line).strip()
        cleaned = re.sub(r"^\s*\d+[.)]\s+", "", cleaned).strip()
        if cleaned:
            lines.append(cleaned)

    ideas = []
    for i, line in enumerate(lines, start=1):
        if ":" in line and len(line.split(":", 1)[0].split()) <= 6:
            name, text = line.split(":", 1)
            ideas.append(Idea(i, name.strip(), text.strip()))
        else:
            ideas.append(Idea(i, f"Idea {i}", line))
    if not ideas:
        raise SystemExit("Could not parse any ideas from the input.")
    return ideas


def normalise_tokens(text: str) -> List[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def jaccard_similarity(a: Iterable[str], b: Iterable[str]) -> float:
    set_a = set(a)
    set_b = set(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def sequence_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def apply_patterns(text: str, patterns: dict[str, list[str]]) -> Counter:
    counts: Counter = Counter()
    for tag, regs in patterns.items():
        if any(re.search(reg, text, flags=re.IGNORECASE) for reg in regs):
            counts[tag] += 1
    return counts


def find_duplicates(ideas: List[Idea]) -> list[tuple[Idea, Idea, float, float]]:
    results = []
    token_map = {idea.idx: normalise_tokens(idea.combined) for idea in ideas}
    for i, a in enumerate(ideas):
        for b in ideas[i + 1:]:
            jac = jaccard_similarity(token_map[a.idx], token_map[b.idx])
            seq = sequence_similarity(a.combined, b.combined)
            if jac >= 0.33 or seq >= 0.72:
                results.append((a, b, jac, seq))
    return sorted(results, key=lambda x: max(x[2], x[3]), reverse=True)


def top_terms(ideas: List[Idea], limit: int = 12) -> list[tuple[str, int]]:
    counter = Counter()
    for idea in ideas:
        counter.update(normalise_tokens(idea.combined))
    return counter.most_common(limit)


def coverage_counts(ideas: List[Idea], patterns: dict[str, list[str]]) -> Counter:
    counter = Counter()
    for idea in ideas:
        counter.update(apply_patterns(idea.combined, patterns))
    return counter


def suggest_regeneration(
    tag_counts: Counter,
    value_counts: Counter,
    channel_counts: Counter,
    total: int,
) -> list[str]:
    suggestions: list[str] = []

    dominant_tags = [tag for tag, count in tag_counts.items() if count / max(total, 1) >= 0.4]
    if dominant_tags:
        joined = ", ".join(dominant_tags)
        suggestions.append(
            f"Generate 3 ideas that do not use these dominant patterns: {joined}."
        )

    if value_counts.get("risk", 0) == 0:
        suggestions.append("Generate 2 ideas where the main value is risk reduction or reassurance.")
    if value_counts.get("time", 0) == 0:
        suggestions.append("Generate 2 ideas where the main value is time compression or effort removal.")
    if value_counts.get("status", 0) == 0:
        suggestions.append("Generate 1 or 2 ideas built around status, recognition, or visible competence.")
    if value_counts.get("access", 0) == 0:
        suggestions.append("Generate 1 or 2 ideas that win through access, channel, or distribution.")
    if sum(channel_counts.values()) == 0:
        suggestions.append("Generate 2 ideas whose wedge is a partner, embedded workflow, or referral channel.")

    if not suggestions:
        suggestions.append("Generate 2 ideas from far analogies in logistics, insurance, or museums.")
        suggestions.append("Generate 2 ideas that change ownership, payment timing, or who carries the risk.")

    return suggestions


def format_markdown(ideas: List[Idea]) -> str:
    duplicate_pairs = find_duplicates(ideas)
    tag_counts = coverage_counts(ideas, TAG_PATTERNS)
    value_counts = coverage_counts(ideas, VALUE_PATTERNS)
    channel_counts = coverage_counts(ideas, CHANNEL_PATTERNS)
    term_counts = top_terms(ideas)
    suggestions = suggest_regeneration(tag_counts, value_counts, channel_counts, len(ideas))

    lines: list[str] = []
    lines.append("# Diversity Audit")
    lines.append("")
    lines.append(f"Ideas analysed: {len(ideas)}")
    lines.append("")

    lines.append("## Likely near-duplicates")
    if duplicate_pairs:
        for a, b, jac, seq in duplicate_pairs[:10]:
            lines.append(
                f"- {a.idx} and {b.idx}: Jaccard {jac:.2f}, sequence {seq:.2f} "
                f"— {a.name} / {b.name}"
            )
    else:
        lines.append("- No obvious near-duplicates detected by the heuristic.")
    lines.append("")

    lines.append("## Dominant repeated patterns")
    if tag_counts:
        for tag, count in tag_counts.most_common():
            lines.append(f"- {tag}: {count}")
    else:
        lines.append("- No repeated cliché patterns detected.")
    lines.append("")

    lines.append("## Coverage signals")
    if value_counts:
        lines.append("- Value types:")
        for tag, count in value_counts.most_common():
            lines.append(f"  - {tag}: {count}")
    else:
        lines.append("- Value types: no strong signals detected")

    if channel_counts:
        lines.append("- Channel signals:")
        for tag, count in channel_counts.most_common():
            lines.append(f"  - {tag}: {count}")
    else:
        lines.append("- Channel signals: no clear wedge language detected")
    lines.append("")

    lines.append("## Repeated terms")
    if term_counts:
        lines.append("- " + ", ".join(f"{term} {count}" for term, count in term_counts))
    else:
        lines.append("- No repeated terms detected.")
    lines.append("")

    lines.append("## Suggested regeneration prompts")
    for item in suggestions:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Notes")
    lines.append(
        "- This is a lightweight heuristic audit. Use it to spot collapse, not to replace judgement."
    )
    lines.append(
        "- If the audit flags many duplicates, regenerate missing mechanism families before scoring."
    )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit idea lists for near-duplicates and dominant patterns.")
    parser.add_argument("path", nargs="?", help="Path to a JSON or text file containing ideas.")
    args = parser.parse_args()

    raw = load_text_from_path_or_stdin(args.path)
    ideas = parse_ideas(raw)
    report = format_markdown(ideas)
    print(report)


if __name__ == "__main__":
    main()

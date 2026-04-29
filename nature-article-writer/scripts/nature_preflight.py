\
#!/usr/bin/env python3
"""
Nature / Nature Portfolio manuscript preflight checker.

This script performs structural, stylistic, and policy-aware checks on a draft.
It is lightweight, stdlib-only, and intended for non-interactive agent use.

Examples:
  python3 scripts/nature_preflight.py --input draft.md --mode nature-article --format text
  python3 scripts/nature_preflight.py --input draft.md --mode portfolio-article --format json
  cat draft.md | python3 scripts/nature_preflight.py --mode nature-letter

Exit codes:
  0  success
  2  usage error or unreadable input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

from prose_metrics import (
    as_json,
    metrics as prose_metrics,
    read_text,
    strip_frontmatter,
    sentences,
    words,
)

SECTION_PATTERNS = {
    "abstract": re.compile(r"^\s{0,3}(?:#+\s*)?abstract\s*$", re.I),
    "summary_paragraph": re.compile(r"^\s{0,3}(?:#+\s*)?(?:summary paragraph|summary)\s*$", re.I),
    "introductory_paragraph": re.compile(r"^\s{0,3}(?:#+\s*)?introductory paragraph\s*$", re.I),
    "introduction": re.compile(r"^\s{0,3}(?:#+\s*)?introduction\s*$", re.I),
    "results": re.compile(r"^\s{0,3}(?:#+\s*)?results\s*$", re.I),
    "discussion": re.compile(r"^\s{0,3}(?:#+\s*)?discussion\s*$", re.I),
    "methods": re.compile(r"^\s{0,3}(?:#+\s*)?(?:online methods|methods)\s*$", re.I),
    "data_availability": re.compile(r"^\s{0,3}(?:#+\s*)?data availability\s*$", re.I),
    "code_availability": re.compile(r"^\s{0,3}(?:#+\s*)?code availability\s*$", re.I),
    "references": re.compile(r"^\s{0,3}(?:#+\s*)?references\s*$", re.I),
    "acknowledgements": re.compile(r"^\s{0,3}(?:#+\s*)?acknowledg(?:e)?ments\s*$", re.I),
    "funding_statement": re.compile(r"^\s{0,3}(?:#+\s*)?funding(?: statement)?\s*$", re.I),
    "author_contributions": re.compile(r"^\s{0,3}(?:#+\s*)?author contributions\s*$", re.I),
    "competing_interests": re.compile(r"^\s{0,3}(?:#+\s*)?(?:competing interests|conflict of interest|conflicts of interest)\s*$", re.I),
    "additional_information": re.compile(r"^\s{0,3}(?:#+\s*)?additional information\s*$", re.I),
    "figure_legends": re.compile(r"^\s{0,3}(?:#+\s*)?figure legends\s*$", re.I),
    "extended_data_legends": re.compile(r"^\s{0,3}(?:#+\s*)?extended data(?: figure| table)? legends\s*$", re.I),
}

MODE_REQUIREMENTS = {
    "nature-article": {
        "sections_required": ["methods", "data_availability", "references", "figure_legends"],
        "sections_recommended": ["code_availability", "funding_statement", "author_contributions", "competing_interests"],
        "opening_type": "summary",
        "opening_target_words_max": 220,
        "title_chars_max": 75,
        "main_headings_allowed": True,
    },
    "nature-letter": {
        "sections_required": ["methods", "data_availability", "references", "figure_legends"],
        "sections_recommended": ["code_availability", "funding_statement", "author_contributions", "competing_interests"],
        "opening_type": "introductory",
        "opening_target_words_max": 220,
        "title_chars_max": 85,
        "main_headings_allowed": False,
    },
    "portfolio-article": {
        "sections_required": ["methods", "data_availability", "references"],
        "sections_recommended": ["results", "discussion", "code_availability", "funding_statement", "author_contributions", "competing_interests", "figure_legends"],
        "opening_type": "abstract",
        "opening_target_words_max": 250,
        "title_chars_max": 120,
        "main_headings_allowed": True,
    },
    "portfolio-letter": {
        "sections_required": ["methods", "data_availability", "references"],
        "sections_recommended": ["code_availability", "funding_statement", "author_contributions", "competing_interests", "figure_legends"],
        "opening_type": "introductory",
        "opening_target_words_max": 220,
        "title_chars_max": 120,
        "main_headings_allowed": False,
    },
}

TITLE_BAD_WORDS = {"novel", "groundbreaking", "transformative", "remarkable", "unprecedented"}
TITLE_ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9-]{1,}\b")
TITLE_PUNCT_RE = re.compile(r"[:;!?]")
BRACKET_CITATION_RE = re.compile(r"\[(?:\d+(?:\s*[-,]\s*\d+)*)\]")
FIGURE_HEADING_RE = re.compile(r"^\s{0,3}(?:#+\s*)?(?:figure|fig\.)\s*\d+\b", re.I)
STATS_HINT_RE = re.compile(r"\b(?:n\s*=|P\s*[<=>]|Student'?s t-test|Mann-Whitney|ANOVA|Wilcoxon|Kruskal|error bars|s\.d\.|s\.e\.m\.|median|mean)\b", re.I)
LEGEND_TITLE_SENTENCE_RE = re.compile(r"^[A-Z].{10,200}[.!?]$")

@dataclass
class Issue:
    severity: str
    code: str
    message: str
    evidence: str = ""
    fix: str = ""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run a structural and stylistic preflight check on a Nature-style manuscript draft."
    )
    p.add_argument("--input", help="Draft file to analyse. If omitted, read from stdin.")
    p.add_argument("--mode", choices=sorted(MODE_REQUIREMENTS), required=True, help="Target manuscript mode.")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return p


def load_text(path: str | None) -> str:
    if path:
        try:
            return read_text(path)
        except FileNotFoundError:
            raise SystemExit(f"Error: input file not found: {path}")
        except OSError as exc:
            raise SystemExit(f"Error: could not read {path}: {exc}")
    data = sys.stdin.read()
    if not data.strip():
        raise SystemExit("Error: no input provided. Use --input FILE or pipe text via stdin.")
    return data


def nonempty_lines(text: str) -> List[str]:
    return [line for line in text.splitlines() if line.strip()]


def normalize_heading(line: str) -> str:
    return re.sub(r"^\s*#+\s*", "", line).strip()


def first_title_line(text: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return normalize_heading(s)
        return s
    return ""


def paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def detect_sections(text: str) -> Dict[str, Tuple[int, int]]:
    lines = text.splitlines()
    hits: List[Tuple[str, int]] = []
    for idx, line in enumerate(lines):
        for name, pat in SECTION_PATTERNS.items():
            if pat.match(line):
                hits.append((name, idx))
                break
    ranges: Dict[str, Tuple[int, int]] = {}
    for i, (name, start) in enumerate(hits):
        end = len(lines) if i + 1 >= len(hits) else hits[i + 1][1]
        ranges[name] = (start, end)
    return ranges


def section_text(text: str, ranges: Dict[str, Tuple[int, int]], name: str) -> str:
    if name not in ranges:
        return ""
    start, end = ranges[name]
    lines = text.splitlines()
    return "\n".join(lines[start + 1:end]).strip()


def get_opening_text(text: str, mode: str, sections: Dict[str, Tuple[int, int]]) -> tuple[str, str]:
    if mode == "nature-article" and "summary_paragraph" in sections:
        return "summary_paragraph", section_text(text, sections, "summary_paragraph")
    if mode == "nature-letter" and "introductory_paragraph" in sections:
        return "introductory_paragraph", section_text(text, sections, "introductory_paragraph")
    if mode == "portfolio-article" and "abstract" in sections:
        return "abstract", section_text(text, sections, "abstract")
    if mode == "portfolio-letter" and "introductory_paragraph" in sections:
        return "introductory_paragraph", section_text(text, sections, "introductory_paragraph")

    title = first_title_line(text)
    paras = [p for p in paragraphs(text) if p != title and len(words(p)) >= 6]
    return "first_paragraph", paras[0] if paras else ""


def contains_reference_like_markers(text: str) -> bool:
    return bool(BRACKET_CITATION_RE.search(text))


def title_checks(title: str, mode: str) -> List[Issue]:
    issues: List[Issue] = []
    limit = MODE_REQUIREMENTS[mode]["title_chars_max"]
    if not title:
        issues.append(Issue("error", "title_missing", "No title line detected.", fix="Add a manuscript title at the start of the document."))
        return issues
    if len(title) > limit:
        issues.append(Issue("warning", "title_too_long", f"Title length is {len(title)} characters; target is <= {limit} for this mode.", evidence=title, fix="Shorten the title and remove non-essential modifiers."))
    lower_words = {w.lower() for w in words(title)}
    bad = sorted(lower_words & TITLE_BAD_WORDS)
    if bad:
        issues.append(Issue("warning", "title_hype", "Title contains evaluative or hype language.", evidence=", ".join(bad), fix="Replace evaluative adjectives with the actual object, process, or finding."))
    if mode.startswith("nature"):
        if TITLE_ACRONYM_RE.search(title):
            issues.append(Issue("warning", "title_acronym", "Nature-style titles usually avoid acronyms unless essential.", evidence=title, fix="Spell out the term or remove the acronym if possible."))
        if TITLE_PUNCT_RE.search(title):
            issues.append(Issue("warning", "title_punctuation", "Nature-style titles usually avoid decorative punctuation such as colons or question marks.", evidence=title, fix="Simplify the title into a single clear clause if possible."))
    return issues


def section_checks(text: str, mode: str, sections: Dict[str, Tuple[int, int]]) -> List[Issue]:
    issues: List[Issue] = []
    reqs = MODE_REQUIREMENTS[mode]
    for sec in reqs["sections_required"]:
        if sec not in sections:
            issues.append(Issue("error", f"missing_{sec}", f"Missing required section: {sec.replace('_', ' ').title()}.", fix=f"Add a {sec.replace('_', ' ').title()} section or mark it as pending."))
    for sec in reqs["sections_recommended"]:
        if sec not in sections:
            issues.append(Issue("note", f"missing_{sec}", f"Recommended section not found: {sec.replace('_', ' ').title()}.", fix=f"Confirm whether a {sec.replace('_', ' ').title()} section is required by the target journal."))
    if not reqs["main_headings_allowed"]:
        for forbidden in ("results", "discussion", "introduction"):
            if forbidden in sections:
                issues.append(Issue("warning", f"heading_policy_{forbidden}", f"{mode} usually reads as a continuous narrative; explicit '{forbidden.title()}' heading detected.", fix="Check whether the target format discourages main-text headings."))
    return issues


def opening_checks(text: str, mode: str, sections: Dict[str, Tuple[int, int]]) -> List[Issue]:
    issues: List[Issue] = []
    label, opening = get_opening_text(text, mode, sections)
    expected_heading = {
        "nature-article": "summary_paragraph",
        "nature-letter": "introductory_paragraph",
        "portfolio-article": "abstract",
        "portfolio-letter": "introductory_paragraph",
    }[mode]
    if expected_heading not in sections:
        issues.append(Issue("warning", "opening_heading_missing", f"Expected opening section not found for {mode}: {expected_heading.replace('_', ' ').title()}.", evidence=label, fix="Add the expected opening section heading or confirm that the fallback first paragraph is acceptable for the target journal."))
    if not opening:
        issues.append(Issue("error", "opening_missing", "Could not find an opening summary/abstract/introduction paragraph.", fix="Add the required opening section for the chosen mode."))
        return issues
    n_words = len(words(opening))
    target_max = MODE_REQUIREMENTS[mode]["opening_target_words_max"]
    if n_words > target_max:
        issues.append(Issue("warning", "opening_too_long", f"Opening section is {n_words} words; target is <= {target_max} for this mode.", evidence=label, fix="Cut low-value background, repeated claims, or non-essential numeric detail."))
    if mode.startswith("nature") and not contains_reference_like_markers(opening):
        issues.append(Issue("note", "opening_references", "Nature-style opening paragraph may need reference markers if this is the final manuscript form.", evidence=label, fix="Add references if the target journal/article type expects them."))
    if mode == "nature-article":
        if sum(1 for t in words(opening) if t.isupper() and len(t) > 1) > 2:
            issues.append(Issue("note", "opening_acronym_load", "Opening summary paragraph contains several acronyms; Nature-style openings are usually lighter on abbreviations.", fix="Spell out or remove non-essential abbreviations in the opening paragraph."))
    return issues


def availability_checks(text: str, sections: Dict[str, Tuple[int, int]]) -> List[Issue]:
    issues: List[Issue] = []
    if "data_availability" in sections:
        dat = section_text(text, sections, "data_availability")
        if "upon request" in dat.lower() and not any(x in dat.lower() for x in ("repository", "accession", "controlled", "available from")):
            issues.append(Issue("warning", "data_vague", "Data Availability statement relies on vague 'upon request' wording.", evidence=dat[:180], fix="State repository, accession, or transparent access conditions if possible."))
    if "code_availability" in sections:
        code = section_text(text, sections, "code_availability")
        if "upon request" in code.lower() and "github" not in code.lower() and "gitlab" not in code.lower() and "zenodo" not in code.lower():
            issues.append(Issue("note", "code_vague", "Code Availability statement may be too vague if custom code is central.", evidence=code[:180], fix="State repository, DOI, or clear release conditions if possible."))
    return issues


def figure_legend_checks(text: str, sections: Dict[str, Tuple[int, int]]) -> List[Issue]:
    issues: List[Issue] = []
    legends = section_text(text, sections, "figure_legends")
    if not legends:
        return issues
    lines = [line.rstrip() for line in legends.splitlines()]
    current_figure = None
    current_block: List[str] = []
    blocks: List[Tuple[str, str]] = []
    for line in lines:
        if FIGURE_HEADING_RE.match(line.strip()):
            if current_figure is not None:
                blocks.append((current_figure, "\n".join(current_block).strip()))
            current_figure = normalize_heading(line)
            current_block = []
        else:
            current_block.append(line)
    if current_figure is not None:
        blocks.append((current_figure, "\n".join(current_block).strip()))

    for fig, block in blocks:
        if not block:
            issues.append(Issue("warning", "legend_empty", f"{fig} has no legend text.", fix="Add a title sentence and panel description."))
            continue
        first_line = next((ln.strip() for ln in block.splitlines() if ln.strip()), "")
        if first_line and not LEGEND_TITLE_SENTENCE_RE.match(first_line):
            issues.append(Issue("note", "legend_title_sentence", f"{fig} does not obviously begin with a brief title sentence.", evidence=first_line[:180], fix="Start the legend with one sentence that names the figure's point."))
        if not STATS_HINT_RE.search(block):
            issues.append(Issue("note", "legend_stats", f"{fig} legend contains no obvious statistics or sample-size cues.", evidence=fig, fix="Check whether n, error bars, centre values, or statistical tests need to be defined."))
    return issues


def citation_checks(text: str) -> List[Issue]:
    issues: List[Issue] = []
    hits = BRACKET_CITATION_RE.findall(text)
    if hits:
        issues.append(Issue("note", "bracket_citations", "Bracket-style citations detected.", evidence=", ".join(hits[:8]), fix="Check whether the target journal wants superscript or another citation format."))
    return issues


def style_checks(text: str) -> List[Issue]:
    issues: List[Issue] = []
    m = prose_metrics(text)
    if m["hype_word_total"] > 0:
        examples = ", ".join(f"{k}({v})" for k, v in list(m["hype_words"].items())[:8])
        issues.append(Issue("warning", "hype_words", "Evaluative or hype words detected.", evidence=examples, fix="Replace adjective-led importance language with concrete claims."))
    if m["generic_phrase_total"] > 0:
        examples = ", ".join(f"{k}({v})" for k, v in list(m["generic_phrases"].items())[:8])
        issues.append(Issue("warning", "generic_phrases", "Generic AI-ish manuscript phrases detected.", evidence=examples, fix="Replace generic phrases with the exact implication or delete them."))
    if m["nominalization_rate"] > 0.045:
        issues.append(Issue("note", "nominalization_rate", f"Nominalization rate is high ({m['nominalization_rate']}).", fix="Turn hidden verbs back into actions where possible."))
    if m["participial_clause_rate"] > 0.18:
        issues.append(Issue("note", "participial_rate", f"Many sentences contain '-ing' clause cues ({m['participial_clause_rate']}).", fix="Break multi-clause sentences into clearer main clauses."))
    if m["transition_opener_rate"] > 0.08:
        issues.append(Issue("note", "transition_rate", f"Transition-opener rate is high ({m['transition_opener_rate']}).", fix="Cut conveyor-belt transitions and let structure carry more of the logic."))
    if m["weak_opener_rate"] > 0.45:
        issues.append(Issue("note", "weak_openers", f"Many sentences begin with weak openers ({m['weak_opener_rate']}).", evidence=", ".join(f"{k}:{v}" for k, v in list(m["top_sentence_openers"].items())[:5]), fix="Vary sentence openings around the object, comparison, or condition rather than repeating pronouns."))
    if m["flatness_score"] > 0.18 and m["sentence_count"] >= 8:
        issues.append(Issue("note", "rhythm_flat", f"Sentence-length variation appears low (flatness score {m['flatness_score']}).", fix="Mix shorter claim sentences with longer explanatory ones."))
    return issues


def ending_checks(text: str) -> List[Issue]:
    issues: List[Issue] = []
    sents = sentences(text)
    if not sents:
        return issues
    last = sents[-1].lower()
    cliches = [
        "opens new avenues",
        "future work",
        "highlight the importance of",
        "underscores the importance of",
        "will be needed to fully understand",
    ]
    for phrase in cliches:
        if phrase in last:
            issues.append(Issue("note", "generic_ending", "Final sentence ends on a generic future-work or importance phrase.", evidence=sents[-1][:220], fix="End on the most defensible implication or boundary condition instead."))
            break
    return issues


def prioritise(issues: List[Issue]) -> List[Issue]:
    order = {"error": 0, "warning": 1, "note": 2}
    return sorted(issues, key=lambda x: (order.get(x.severity, 9), x.code, x.message))


def render_text(mode: str, title: str, opening_label: str, metrics: dict, issues: List[Issue]) -> str:
    lines = []
    lines.append("Nature-style preflight report")
    lines.append("============================")
    lines.append(f"Mode: {mode}")
    lines.append(f"Title: {title or '[missing]'}")
    lines.append("")
    lines.append("Document profile")
    lines.append("----------------")
    lines.append(f"- words: {metrics['word_count']}")
    lines.append(f"- sentences: {metrics['sentence_count']}")
    lines.append(f"- paragraphs: {metrics['paragraph_count']}")
    lines.append(f"- mean sentence length: {metrics['mean_sentence_words']} words")
    lines.append(f"- sentence-length variation: {metrics['stdev_sentence_words']}")
    lines.append(f"- nominalization rate: {metrics['nominalization_rate']}")
    lines.append(f"- participial-clause rate: {metrics['participial_clause_rate']}")
    lines.append(f"- transition-opener rate: {metrics['transition_opener_rate']}")
    lines.append(f"- weak-opener rate: {metrics['weak_opener_rate']}")
    lines.append(f"- opening source: {opening_label}")
    lines.append("")
    lines.append("Prioritised issues")
    lines.append("------------------")
    if not issues:
        lines.append("- No major issues detected by the bundled heuristics. Review journal-specific details manually.")
    else:
        for issue in issues:
            line = f"- [{issue.severity.upper()}] {issue.message}"
            lines.append(line)
            if issue.evidence:
                lines.append(f"  evidence: {issue.evidence}")
            if issue.fix:
                lines.append(f"  fix: {issue.fix}")
    lines.append("")
    lines.append("Interpretation")
    lines.append("--------------")
    lines.append("Use this report to fix structure first, then claim calibration, then line-level prose. These heuristics are advisory; they are meant to surface likely weak spots, not to replace scientific judgement.")
    return "\n".join(lines)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    raw = load_text(args.input)
    text = strip_frontmatter(raw)
    title = first_title_line(text)
    sections = detect_sections(text)
    opening_label, _ = get_opening_text(text, args.mode, sections)
    m = prose_metrics(text)

    issues: List[Issue] = []
    issues.extend(title_checks(title, args.mode))
    issues.extend(section_checks(text, args.mode, sections))
    issues.extend(opening_checks(text, args.mode, sections))
    issues.extend(availability_checks(text, sections))
    issues.extend(figure_legend_checks(text, sections))
    issues.extend(citation_checks(text))
    issues.extend(style_checks(text))
    issues.extend(ending_checks(text))
    issues = prioritise(issues)

    payload = {
        "mode": args.mode,
        "title": title,
        "opening_source": opening_label,
        "metrics": m,
        "issues": [asdict(i) for i in issues],
        "summary": {
            "errors": sum(1 for i in issues if i.severity == "error"),
            "warnings": sum(1 for i in issues if i.severity == "warning"),
            "notes": sum(1 for i in issues if i.severity == "note"),
            "total": len(issues),
        },
    }

    if args.format == "json":
        print(as_json(payload))
    else:
        print(render_text(args.mode, title, opening_label, m, issues))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

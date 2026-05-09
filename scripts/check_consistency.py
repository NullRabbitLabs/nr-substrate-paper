#!/usr/bin/env python3
"""
Consistency checker for the nr-substrate-paper working draft.

Encodes the inconsistency patterns surfaced in manual review cycles:
em-dashes, stale state phrases, self-references, forbidden absolute
paths, MC-N coverage, D-NNN coverage, Appendix B title range,
bibliography citation/definition cross-check, count-phrase
consistency (e.g., "eleven contributions" matching the actual MC
count), §5.1.1 principle count, §8.6 upgrade-incident count,
mutually-exclusive state claims (e.g., nr-bundle-spec
"private until X" vs "published Y"), and §-cross-reference
resolution.

Run from repo root:

    python3 scripts/check_consistency.py
    python3 scripts/check_consistency.py --paper paper.md --bib bibliography.bib

Exit code 0 if all checks pass; 1 if any FAIL; 2 on usage error.

Severity levels:
    FAIL    paper-text issue worth fixing before publication
    WARN    likely an issue but may be intentional; eyeball it

Stdlib only; no external dependencies.
"""

import argparse
import re
import sys
from pathlib import Path


class Result:
    def __init__(self) -> None:
        self.findings: list[tuple[str, str, int | None, str]] = []

    def fail(self, check: str, line: int | None, msg: str) -> None:
        self.findings.append(("FAIL", check, line, msg))

    def warn(self, check: str, line: int | None, msg: str) -> None:
        self.findings.append(("WARN", check, line, msg))

    def report(self, paper_name: str) -> int:
        if not self.findings:
            print(f"OK: all consistency checks passed against {paper_name}")
            return 0

        for sev, check, line, msg in self.findings:
            loc = f"{paper_name}:{line}" if line else paper_name
            print(f"{sev:<4} [{check}] {loc}: {msg}")

        fails = sum(1 for f in self.findings if f[0] == "FAIL")
        warns = sum(1 for f in self.findings if f[0] == "WARN")
        print()
        print(f"Summary: {fails} FAIL, {warns} WARN")
        return 1 if fails else 0


def line_of(text: str, pos: int) -> int:
    return text[:pos].count("\n") + 1


def check_em_dashes(text: str, r: Result) -> None:
    """Paper convention is hyphen, not em-dash."""
    for i, line in enumerate(text.splitlines(), 1):
        if "\u2014" in line:
            snippet = line.strip()[:80]
            r.fail("em-dash", i, snippet)


def check_self_references(text: str, r: Result) -> None:
    """'the substrate paper' as self-reference. Descriptors
    'substrate-paper material' and 'substrate-paper-grade' are OK."""
    pattern = re.compile(r"\bthe substrate paper\b", re.IGNORECASE)
    for m in pattern.finditer(text):
        r.fail(
            "self-reference",
            line_of(text, m.start()),
            "'the substrate paper' - convert to 'this paper' / 'we'",
        )


def check_stale_state(text: str, r: Result) -> None:
    """Stale state phrases that should have been swept after cycle close."""
    needles = [
        ("Joint Outcome", "use 'Joint A/B/C' (no 'Outcome' qualifier)"),
        ("in flight", "this cycle has likely closed - flip to 'closed YYYY-MM-DD'"),
    ]
    for needle, hint in needles:
        pattern = re.compile(re.escape(needle), re.IGNORECASE)
        for m in pattern.finditer(text):
            r.fail("stale-state", line_of(text, m.start()), f"'{needle}': {hint}")


def check_forbidden_paths(text: str, r: Result) -> None:
    """Absolute filesystem paths that leak local environment."""
    patterns = [
        (r"/home/[a-z]+/", "absolute /home/ path"),
        (r"/Users/[A-Za-z]+/", "absolute /Users/ path"),
        (r"\bclaude-wd\b", "claude working-directory path"),
        (r"/data/cargo\b", "local /data/cargo build path"),
        (r"/data/claude\b", "local /data/claude path"),
        (r"/tmp/[a-z]", "/tmp/ path"),
    ]
    for pat, label in patterns:
        regex = re.compile(pat)
        for m in regex.finditer(text):
            r.fail(
                "forbidden-path",
                line_of(text, m.start()),
                f"{label}: {m.group()}",
            )


def check_mc_coverage(text: str, r: Result) -> tuple[set[str], set[str]]:
    """All MC-N references resolve to a definition."""
    defs = set(re.findall(r"^\*\*MC-(\d+)", text, flags=re.MULTILINE))
    refs = set(re.findall(r"\bMC-(\d+)\b", text))
    undefined = refs - defs

    for n in sorted(undefined, key=int):
        r.fail("mc-coverage", None, f"MC-{n} referenced but never defined")

    return defs, refs


def check_dnnn_coverage(text: str, r: Result) -> None:
    """All D-NNN body references appear in Appendix B; title range matches."""
    body_dnnn = set(re.findall(r"\bD-(\d{3})\b", text))

    apdx_b_match = re.search(
        r"# Appendix B[^\n]*\n(.*?)(?=^# |\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if apdx_b_match is None:
        r.fail("dnnn-coverage", None, "Appendix B not found")
        return
    apdx_b = apdx_b_match.group(1)
    table_dnnn = set(re.findall(r"\|\s*D-(\d{3})\b", apdx_b))

    for n in sorted(body_dnnn - table_dnnn, key=int):
        r.fail(
            "dnnn-coverage",
            None,
            f"D-{n} referenced in body but missing from Appendix B table",
        )

    title_match = re.search(
        r"# Appendix B[^\n]*?D-(\d{3})\s*(?:\u2192|->|-)\s*D-(\d{3})",
        text,
    )
    if title_match and table_dnnn:
        title_min, title_max = title_match.group(1), title_match.group(2)
        actual = sorted(table_dnnn, key=int)
        actual_min, actual_max = actual[0], actual[-1]
        if title_min != actual_min or title_max != actual_max:
            r.fail(
                "dnnn-title",
                line_of(text, title_match.start()),
                f"Appendix B title says D-{title_min} -> D-{title_max} "
                f"but table contains D-{actual_min} -> D-{actual_max}",
            )


def check_bib_keys(text: str, bib_text: str, r: Result) -> None:
    """All paper bib citations resolve; flag unused bib entries as WARN.

    Citations may span lines, e.g. ``[sommer2010outside,\n  buczak2016survey]``,
    so the inner character class includes whitespace (``\\s``).
    """
    citations: set[str] = set()
    for m in re.finditer(r"\[([a-zA-Z][a-zA-Z0-9_,\s-]*)\]", text):
        for raw in re.split(r",\s*", m.group(1)):
            key = raw.strip()
            if re.match(
                r"^("
                r"[a-z][a-z0-9_]*[0-9]{4}[a-z][a-z0-9]*"
                r"|cve-[0-9]{4}-[0-9]+"
                r"|bundle_spec_v[0-9_]+"
                r")$",
                key,
            ):
                citations.add(key)

    defs = set(re.findall(r"@[a-z]+\{([^,\s]+)\s*,", bib_text))

    for k in sorted(citations - defs):
        r.fail("bib-key", None, f"citation [{k}] has no entry in bibliography.bib")
    for k in sorted(defs - citations):
        r.warn("bib-key", None, f"bib entry {k} has no citation in paper.md")


_NUM_TO_WORD = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
}
_WORDS = set(_NUM_TO_WORD.values())


def check_count_phrases(text: str, r: Result) -> None:
    """Aggregate count phrases match the actual MC count."""
    mc_lines = re.findall(r"^\*\*MC-(\d+)(?:\s*\(([^)]+)\))?", text, flags=re.MULTILINE)
    full_grade = [n for n, qual in mc_lines if "footnote" not in qual.lower()]
    expected = _NUM_TO_WORD.get(len(full_grade))
    if not expected:
        return

    patterns = [
        (
            r"(\w+) substrate-paper-grade methodology contributions",
            "§8.7 intro",
        ),
        (
            r"the (\w+) contributions generalise",
            "§8.7 Transferability",
        ),
        (
            r"(\w+) Step-11 \+ Phase-1 cycle methodology contributions",
            "§9 conclusion",
        ),
    ]
    for pat, label in patterns:
        for m in re.finditer(pat, text):
            word = m.group(1).lower()
            if word in _WORDS and word != expected:
                r.fail(
                    "count-phrase",
                    line_of(text, m.start()),
                    f"{label} says '{word}' but {len(full_grade)} "
                    f"substrate-paper-grade MCs defined (expected '{expected}')",
                )


def check_principles_count(text: str, r: Result) -> None:
    """§5.1.1 'X methodological principles' heading and intro match."""
    section = re.search(
        r"### §5\.1\.1[^\n]*\n(.*?)(?=^## |^### |\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if not section:
        return
    block = section.group(1)
    actual = len(re.findall(r"^(\d+)\.\s+\*\*", block, flags=re.MULTILINE))
    if actual == 0:
        return

    word_cap = {n: w.capitalize() for n, w in _NUM_TO_WORD.items()}
    expected = word_cap.get(actual)
    if not expected:
        return

    heading = re.search(r"### §5\.1\.1\s+(\w+) methodological principles", text)
    if heading and heading.group(1) != expected:
        r.fail(
            "principles-count",
            line_of(text, heading.start()),
            f"§5.1.1 heading says '{heading.group(1)}' but {actual} "
            f"principles found (expected '{expected}')",
        )

    intro = re.search(r"(\w+) foundational commitments anchor the methodology", text)
    if intro and intro.group(1) != expected:
        r.fail(
            "principles-count",
            line_of(text, intro.start()),
            f"§5.1.1 intro says '{intro.group(1)}' foundational commitments "
            f"but {actual} principles found",
        )


def check_upgrade_incidents(text: str, r: Result) -> None:
    """§8.6 'X upgrade incidents' matches the actual count."""
    section = re.search(
        r"## §8\.6[^\n]*\n(.*?)(?=^## )",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if not section:
        return
    block = section.group(1)
    heading = re.search(r"\*\*(\w+) upgrade incidents?\*\*", block)
    if not heading:
        return
    actual = len(re.findall(r"^(\d+)\.\s+\*\*", block, flags=re.MULTILINE))
    if actual == 0:
        return

    word_cap = {n: w.capitalize() for n, w in _NUM_TO_WORD.items()}
    expected = word_cap.get(actual, str(actual))
    if heading.group(1) != expected:
        r.fail(
            "upgrade-incidents",
            None,
            f"§8.6 heading says '{heading.group(1)} upgrade incidents' "
            f"but {actual} numbered items found",
        )


def check_mutex_states(text: str, r: Result) -> None:
    """nr-bundle-spec must not be both 'private until X' and unqualified
    'published Y' simultaneously - either say 'tagged Y' or cross-ref §3.4."""
    has_private = re.search(
        r"private repo? until 2026-06-05",
        text,
    )
    if not has_private:
        return
    for i, line in enumerate(text.splitlines(), 1):
        if (
            re.search(r"\bpublished 2026-05-06\b", line)
            and "tagged" not in line
            and "access state per" not in line
        ):
            r.fail(
                "mutex-state",
                i,
                "claims 'published 2026-05-06' but elsewhere repo is "
                "'private until 2026-06-05' - say 'tagged 2026-05-06' "
                "and cross-ref §3.4",
            )


def check_section_xrefs(text: str, r: Result) -> None:
    """§X.Y cross-refs resolve to existing section headings (any prefix match)."""
    headings: set[str] = set()
    for m in re.finditer(
        r"^#{1,4}\s+(?:§|Appendix\s+)?([A-Z]?\d+(?:\.\d+)*)\b",
        text,
        flags=re.MULTILINE,
    ):
        headings.add(m.group(1).rstrip("."))

    refs = set(re.findall(r"§(\d+(?:\.\d+)*)", text))
    missing: list[str] = []
    for ref in refs:
        parts = ref.split(".")
        if any(".".join(parts[:i]) in headings for i in range(len(parts), 0, -1)):
            continue
        missing.append(ref)
    for ref in sorted(set(missing)):
        r.warn(
            "section-xref",
            None,
            f"§{ref} referenced but no matching heading found",
        )


def check_published_date_consistency(text: str, r: Result) -> None:
    """nr-bundle-spec dates: tagged 2026-05-06; private until 2026-06-05.
    Flag any other ambiguous 'published 2026-05-06' phrasing."""
    # Already partially covered by check_mutex_states; this is a softer pass
    pass


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--paper", default="paper.md", help="path to paper.md")
    p.add_argument("--bib", default="bibliography.bib", help="path to bibliography.bib")
    args = p.parse_args()

    paper = Path(args.paper)
    bib = Path(args.bib)
    if not paper.exists():
        print(f"error: {paper} not found", file=sys.stderr)
        return 2
    if not bib.exists():
        print(f"error: {bib} not found", file=sys.stderr)
        return 2

    text = paper.read_text(encoding="utf-8")
    bib_text = bib.read_text(encoding="utf-8")

    r = Result()
    check_em_dashes(text, r)
    check_self_references(text, r)
    check_stale_state(text, r)
    check_forbidden_paths(text, r)
    check_mc_coverage(text, r)
    check_dnnn_coverage(text, r)
    check_bib_keys(text, bib_text, r)
    check_count_phrases(text, r)
    check_principles_count(text, r)
    check_upgrade_incidents(text, r)
    check_mutex_states(text, r)
    check_section_xrefs(text, r)

    return r.report(str(paper))


if __name__ == "__main__":
    sys.exit(main())

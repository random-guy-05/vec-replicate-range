"""Generate descriptive paired reports from a tidy replicate-score CSV."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Iterable


REQUIRED_COLUMNS = ("candidate", "board", "replicate", "score")


@dataclass(frozen=True)
class Score:
    candidate: str
    board: str
    replicate: str
    value: float


def read_scores(path: Path) -> list[Score]:
    """Read and validate input rows, reporting the source line on errors."""
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise ValueError(f"cannot open {path}: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("input is empty or has no CSV header")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError("missing required column(s): " + ", ".join(missing))

        scores: list[Score] = []
        seen: set[tuple[str, str, str]] = set()
        for line_number, row in enumerate(reader, start=2):
            candidate = (row.get("candidate") or "").strip()
            board = (row.get("board") or "").strip()
            replicate = (row.get("replicate") or "").strip()
            raw_score = (row.get("score") or "").strip()
            if not candidate or not board or not replicate:
                raise ValueError(
                    f"line {line_number}: candidate, board and replicate must be non-empty"
                )
            try:
                value = float(raw_score)
            except ValueError as exc:
                raise ValueError(f"line {line_number}: score must be numeric") from exc
            if not math.isfinite(value):
                raise ValueError(f"line {line_number}: score must be finite")
            key = (board, candidate, replicate)
            if key in seen:
                raise ValueError(
                    f"line {line_number}: duplicate candidate/board/replicate row "
                    f"({candidate!r}, {board!r}, {replicate!r})"
                )
            seen.add(key)
            scores.append(Score(candidate, board, replicate, value))

    if not scores:
        raise ValueError("input has a header but no score rows")
    return scores


def grouped_scores(scores: Iterable[Score]) -> dict[str, dict[str, dict[str, float]]]:
    grouped: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in scores:
        grouped[row.board][row.candidate][row.replicate] = row.value
    return grouped


def table_cell(value: str) -> str:
    """Keep user-provided labels from breaking the Markdown table layout."""
    return value.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def markdown_report(scores: list[Score], source: str) -> str:
    """Build a Markdown report with only descriptive summaries."""
    grouped = grouped_scores(scores)
    out = [
        "# VEC Replicate Range report",
        "",
        f"Input: `{source}`  ",
        f"Rows: {len(scores)}  ",
        f"Boards: {len(grouped)}  ",
        "",
        "> **Descriptive only.** Two biological replicates do not support a population-level "
        "uncertainty estimate or a significance test. This report does not override the "
        "Challenge's official ranking.",
        "",
    ]

    for board in sorted(grouped):
        candidates = grouped[board]
        out.extend([f"## {board}", ""])
        out.append("| Candidate | n | Mean | Min | Max | Range | Replicates |")
        out.append("|---|---:|---:|---:|---:|---:|---|")
        for candidate in sorted(candidates):
            values = candidates[candidate]
            numbers = list(values.values())
            out.append(
                f"| {table_cell(candidate)} | {len(numbers)} | {fmean(numbers):.4f} | "
                f"{min(numbers):.4f} | {max(numbers):.4f} | "
                f"{max(numbers) - min(numbers):.4f} | "
                f"{', '.join(table_cell(name) for name in sorted(values))} |"
            )
        out.append("")

        names = sorted(candidates)
        if len(names) > 1:
            out.extend(
                [
                    "### Paired comparisons",
                    "",
                    "Only replicate IDs present for both candidates are compared. “A reversal” "
                    "means the sign of the score difference changes across shared replicate IDs.",
                    "",
                    "| A | B | Shared replicates | A wins | Ties | B wins | Mean paired Δ (A−B) | Reversal |",
                    "|---|---|---:|---:|---:|---:|---:|---|",
                ]
            )
            for index, name_a in enumerate(names):
                for name_b in names[index + 1 :]:
                    common = sorted(set(candidates[name_a]) & set(candidates[name_b]))
                    deltas = [
                        candidates[name_a][replicate] - candidates[name_b][replicate]
                        for replicate in common
                    ]
                    wins = sum(delta > 0 for delta in deltas)
                    ties = sum(delta == 0 for delta in deltas)
                    losses = sum(delta < 0 for delta in deltas)
                    reversal = "yes" if wins and losses else "no"
                    mean_delta = f"{fmean(deltas):.4f}" if deltas else "n/a"
                    out.append(
                        f"| {table_cell(name_a)} | {table_cell(name_b)} | {len(common)} | {wins} | {ties} | "
                        f"{losses} | {mean_delta} | {reversal} |"
                    )
            out.append("")

    out.extend(
        [
            "## Interpretation",
            "",
            "Ranges and paired reversals describe only the records supplied. They are not "
            "confidence intervals, p-values, or evidence that a method generalizes to all "
            "embryos. If the official board reports a fixed-replicate rank, that remains the "
            "rank. Use this report as context when reviewing completed predictions, within "
            "the Challenge rules.",
            "",
            "Sources: [Challenge data page](https://virtualembryo.ai/challenge/data) · "
            "[Challenge rules](https://virtualembryo.ai/challenge/rules).",
            "",
        ]
    )
    return "\n".join(out)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vec-replicate-range",
        description="Create a descriptive paired report from VEC replicate scores.",
        epilog=(
            "With two biological replicates, the output is descriptive only; "
            "it does not estimate population uncertainty or replace official ranking."
        ),
    )
    parser.add_argument("csv", type=Path, help="input CSV with candidate, board, replicate, score")
    parser.add_argument("--out", type=Path, help="write Markdown report to this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        scores = read_scores(args.csv)
        report = markdown_report(scores, str(args.csv))
        if args.out:
            args.out.write_text(report, encoding="utf-8")
        else:
            sys.stdout.write(report)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

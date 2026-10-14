# VEC Replicate Range

**A small, offline report for seeing how Task 3 scores vary across the two biological validation replicates.**

Task 3's Gata4 validation target has two biological replicates. The Challenge reports the same prediction against each replicate and publishes their score difference. That difference is useful context when two methods are close: it shows how much the comparison moves across these two embryos. This tool turns a hand-prepared score table into a compact, paired report.

## What it does

- Checks a plain CSV for missing fields, non-finite scores and duplicate candidate/board/replicate rows.
- Summarises each candidate's mean, minimum, maximum and range across the supplied replicates.
- Compares candidates only on replicate IDs present for both, and flags pairwise ordering reversals.
- Writes a self-contained Markdown report with the input coverage and limitations stated up front.

It uses only Python's standard library and does not read or modify H5AD files, contact the Challenge, or infer hidden target data.

## Input

Prepare a CSV with one row per candidate, board and biological replicate:

```csv
candidate,board,replicate,score
baseline,T3:gata4,replicate-1,61.2
baseline,T3:gata4,replicate-2,58.7
method-a,T3:gata4,replicate-1,63.1
method-a,T3:gata4,replicate-2,57.9
```

Use the overall score for each replicate, with higher values meaning better performance. Do not mix boards or score scales under one board name. `examples/synthetic_scores.csv` is invented data for a quick orientation; it is clearly labelled synthetic and must not be mistaken for Challenge results.

## Run

Python 3.10 or later; no install step or third-party package is needed.

```bash
python -m vec_replicate_range examples/synthetic_scores.csv --out report.md
```

From another directory, point Python at the repository root:

```bash
PYTHONPATH=/path/to/vec-replicate-range \
  python -m vec_replicate_range scores.csv --out report.md
```

Omit `--out` to print the report to standard output. Use `--help` for options.

## Reading the report responsibly

The two Gata4 embryos are **two observed biological replicates**, not a sample large enough to estimate a population distribution or support a significance test. A range, a reversal, or a mean here is descriptive only. The report never calculates a p-value, confidence interval, or “winner.” The official board's ranking remains the Challenge's ranking; this report is supplementary context for understanding replicate sensitivity.

This tool compares score records you provide. It does not create predictions from returned scores. Challenge rules permit returned scores to help choose among completed predictions, but prohibit using them to recover held-out properties and build those properties into a prediction.

## Sources

- [Challenge data page — Task 3 replicates and scoring](https://virtualembryo.ai/challenge/data)
- [Challenge rules — use of returned scores](https://virtualembryo.ai/challenge/rules)

The data page describes the two Gata4 validation replicates and says their score difference is published alongside the result. The rules page explains the boundary between using returned scores to choose a prediction and recovering held-out information to construct one.

## License

MIT. See [LICENSE](LICENSE).

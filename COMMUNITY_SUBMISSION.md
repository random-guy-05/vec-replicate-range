# Community Contribution submission

- **Kind:** build
- **Title:** VEC Replicate Range — a paired Task 3 biological-replicate sensitivity report
- **Public link:** https://github.com/random-guy-05/vec-replicate-range
- **What it is, and who it helps:** An offline, dependency-free Python CLI for participants comparing completed Task 3 validation results across the two Gata4 biological replicates. It validates a tidy score CSV, summarizes per-candidate ranges, and flags pairwise rank reversals on shared replicates. Its documentation distinguishes biological replicate variation from cell-resampling uncertainty and clearly prohibits inferential claims from n=2. It complements per-cell bootstrap and metric diagnostics by addressing embryo-to-embryo sensitivity.
- **How someone else runs it:** `python -m vec_replicate_range scores.csv --out report.md` (Python 3.10+, no dependencies; set `PYTHONPATH` to the repository root when running outside it).
- **Credit:** Arnav Mana

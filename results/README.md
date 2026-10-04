# Recorded result tables

These files preserve saved notebook outputs and identify their original cells.
Cell indices are **zero-based**. The original analyses were not rerun for this
publication edition. Substantive cells from both original notebooks are consolidated
in `../notebooks/oregano-study.ipynb`, with original-source and original-cell
metadata. `provenance.json` records original notebook SHA-256 hashes, sources,
derivations, and caveats.

| File | Contents | Original evidence |
| --- | --- | --- |
| `entity_counts.csv` | 11 entity classes and their instance counts | Assessment 1, cell 33 |
| `relation_counts.csv` | 17 retained predicates and assertion counts | Assessment 1, cell 28 |
| `relation_coverage.csv` | 187 historical entity/relation participation values and derived fractions | Assessment 1, cell 36 |
| `candidate_paths.csv` | Three paths with matching disease UMLS and indication SIDER codes | Assessment 2, cell 30 |
| `trioxide_candidate_paths.csv` | Three additional arsenic trioxide paths | Assessment 2, cell 35; saved OWL record checks |
| `bayesian_rankings.csv` | 15 saved top-three counts, compound identifiers, corrected disease labels, and original prose labels | Assessment 2, cells 58, 67, 74, 81, 88; associated metadata outputs |
| `summary_metrics.csv` | Graph, candidate-pool, and Bayesian-subset sizes | Per-row source cells |
| `workflow.csv` | Six stages used by the process figure | Per-row source cells |
| `graph_assets.csv` | Node/edge counts and provenance for eight saved graph views | Exported HTML datasets |

The coverage fractions divide the saved participation count by the corresponding
entity count. The original coverage query lacks `DISTINCT`; these fractions are
historical descriptive values rather than independently recomputed coverage.

Disease IDs and saved UMLS values identify the observed Bayesian states. Four
original prose labels disagreed with those identifiers; corrected labels and
NCBI MedGen source links appear alongside the historical labels. Compound IDs
were matched to saved NPASS attributes by a read-only lookup in the original OWL.
Unnamed compound records retain NPASS identifiers rather than guessed drug names.

Ranking values are **raw posterior sample counts**, not clinical probabilities.
Only the saved top-three rows are available for each disease; the full posterior
trace and a verified denominator are not included. Indication-code matches recover
recorded indication associations without independent clinical validation, and
additional graph paths are unvalidated
candidates rather than demonstrated treatments.

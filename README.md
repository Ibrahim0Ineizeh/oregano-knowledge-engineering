# OREGANO: from knowledge graph construction to candidate ranking

**Ibrahim Ineizeh** · Knowledge Engineering · Combined study and archival edition

I started by constructing an ontology from the OREGANO dataset and exploring its structure. I then used the same graph to search for indirect compound–disease connections and build a Bayesian model for ranking compounds. This repository brings both stages together and explains the decisions, findings, and limitations along the way.

![The project workflow](figures/workflow.png)

| Constructed graph | Path search | Bayesian subset |
| --- | --- | --- |
| 189,847 asserted entity instances | 9,234 compounds without a recorded direct treatment relation in the searched set | 60 compounds and 1,190 disease nodes |
| 11 entity classes; 17 object relations | 3 paths with matching indication identifiers | 3 recorded rankings for each of 5 disease nodes |

The results are exploratory. Graph connections and rankings under hand-set probabilities generate hypotheses; they do not establish treatment efficacy. The archived results also exposed disease-label errors in the original discussion, which are corrected and documented here.

## Read the study

- [Combined report](report.md) — the complete account of my process, findings, and reflection.
- [PDF report](output/pdf/oregano-study.pdf) — a formatted version for reading or sharing.
- [Combined notebook](notebooks/oregano-study.ipynb) — code and historical saved outputs from both stages.
- [Interactive graph gallery](visualizations/index.html) — open locally in a browser after downloading the repository.
- [Recorded results](results/) — tables behind the figures, with source cell references.

![Recorded compound rankings for the five observed disease nodes](figures/posterior_rankings.png)

The bars show **saved sample counts**, with disease labels checked against the identifiers used by the model. Unnamed compounds retain their NPASS identifiers. The complete posterior samples are unavailable, so these counts are not presented as treatment probabilities.

## Reproduce or inspect

The report, figures, result tables, and graph gallery can be read without downloading the source dataset. GitHub does not run the notebook's interactive HTML views; download the package to open those views locally.

To run the analysis, use Python 3.12 and place the original OREGANO V2.1 TSV files in `data/`. Follow the [setup and reproducibility notes](docs/reproducibility.md). Stage 1 regenerates the ontology needed by Stage 2. The approximately 860 MB ontology and source TSV files are excluded from this publication package.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab notebooks/oregano-study.ipynb
```

The stored notebook outputs come from the original assessment runs. The combined notebook has been checked structurally and for code syntax; the full analysis has not been rerun for this edition because the source TSV files are absent.

## Repository contents

```text
report.md              Combined research account
notebooks/             One combined analysis notebook
results/               Recorded tables and provenance
figures/               Static PNG and SVG figures
visualizations/        Local interactive graph views and vendor assets
docs/                  Setup, editorial changes, and publication guide
scripts/               Figure, notebook, and PDF build scripts
output/pdf/            Formatted report
data/                  Data placement instructions; no source dataset
```

This is an archival edition of coursework carried out in 2025, prepared for publication on 4 October 2026. See the [publication guide](docs/publishing.md) to upload this folder and then archive the GitHub repository. Local originals are preserved outside this package.

## Attribution

The underlying dataset is the work of Boudin, Diallo, Drancé, and Mougin: [*The OREGANO knowledge graph for computational drug repurposing*](https://doi.org/10.1038/s41597-023-02757-0), *Scientific Data* 10, 871 (2023). Dataset access and version details are described in [data/README.md](data/README.md).

I used AI assistance in the original assessments for SPARQL, language correction, and biomedical interpretation; the second assessment explicitly used Gemini for disease and compound descriptions. Codex assisted with the combined edition's organization, wording, visual presentation, and evidence checks. Corrections and unresolved issues are recorded in the [report](report.md) and [editorial notes](docs/editorial-notes.md).

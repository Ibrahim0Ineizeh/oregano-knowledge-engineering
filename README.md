# OREGANO: from knowledge graph construction to candidate ranking

**Ibrahim Ineizeh** · Knowledge Engineering · Archived study

I started by constructing an ontology from the OREGANO dataset and exploring its structure. I then used the same graph to search for indirect compound–disease connections and build a Bayesian model for ranking compounds. This repository brings both assessments together and explains my process, findings, and results.

![The project workflow](figures/workflow.png)

The recorded graph contains **189,847 entity instances** and **816,481 object relation assertions**. The path search returned three examples with matching indication identifiers, and a restricted Bayesian model ranked compounds for five disease nodes. These are exploratory findings based on graph connections and hand-set model weights; they do not establish treatment efficacy.

## Read the study

- [Combined report](report.md) — the complete account of the methods, findings, corrections, and reflection.
- [PDF report](output/pdf/oregano-study.pdf) — the formatted report for reading or sharing.
- [Combined notebook](notebooks/oregano-study.ipynb) — both stages' code and historical saved outputs.
- [Interactive graph gallery](visualizations/index.html) — download the repository and open this file locally.
- [Recorded results](results/) — the CSV tables and source provenance behind the figures.

![Recorded compound rankings for the five observed disease nodes](figures/posterior_rankings.png)

The bars show saved sample counts. Disease labels follow the identifiers used by the model; unnamed compounds retain their NPASS identifiers. The full posterior samples are unavailable, so the counts are not presented as treatment probabilities.

## Run or rebuild

The report and visuals can be read without downloading the dataset. To run the analysis, use Python 3.12 and the original OREGANO V2.1 input files. The [setup guide](docs/reproducibility.md) contains the environment commands, required files, data sources, and rebuild instructions.

The notebook outputs are retained from the original runs. The full analysis has not been rerun for this edition because the source TSV files are absent. Source cells and hashes are recorded in the notebook metadata and [result provenance](results/provenance.json).

## Attribution

The underlying dataset is the work of Boudin, Diallo, Drancé, and Mougin: [*The OREGANO knowledge graph for computational drug repurposing*](https://doi.org/10.1038/s41597-023-02757-0), *Scientific Data* 10, 871 (2023).

I used AI assistance in the original assessments for SPARQL, language correction, and biomedical interpretation; the second assessment explicitly used Gemini for disease and compound descriptions. Codex assisted with this edition's organization, wording, visuals, and evidence checks. The [report](report.md) gives the full acknowledgments and discusses the identifier corrections and remaining limitations.

This repository preserves coursework carried out in 2025, prepared as a combined archival edition on 4 October 2026.

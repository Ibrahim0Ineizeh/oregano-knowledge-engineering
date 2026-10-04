# Setup and reproducibility

The [report](../report.md) explains the methods, findings, and limitations. This guide covers running the notebook and rebuilding its presentation files.

## Environment and data

Use Python 3.12 with the pinned packages in `requirements.txt`, derived from the original second-stage Conda export:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p data
jupyter lab notebooks/oregano-study.ipynb
```

Before running the notebook, place these files directly under `data/`:

```text
ACTIVITY.tsv       COMPOUND.tsv       DISEASES.tsv
EFFECT.tsv         GENES.tsv          INDICATION.tsv
PATHWAYS.tsv       PHENOTYPES.tsv     SIDE_EFFECT.tsv
TARGET.tsv         OREGANO_V2.1.tsv
```

The study uses the **OREGANO V2.1 assessment distribution**. See the [OREGANO source repository](https://gitub.u-bordeaux.fr/erias/oregano) and [dataset paper](https://doi.org/10.1038/s41597-023-02757-0). Use the original input version for the closest comparison; a current upstream download may have different identifiers, columns, or results. Follow the upstream dataset terms. The source TSV files and large generated ontology are excluded from this repository.

Run the notebook sequentially. Stage 1 writes `data/oregano.owl`; Stage 2 loads it. Generated notebook graphs go to `visualizations/generated/`. The notebook resolves paths from the repository root or its `notebooks/` directory.

Allow several GB of available memory: the largest saved probability tensor alone was approximately 807 MB. Each of the five sampling calls requests 1,000,000 draws per chain and 10,000 tuning iterations, so a complete run is expensive.

## Reading the retained results

The notebook contains historical saved outputs, which were not regenerated after portability and entity-ordering fixes. A new run may therefore produce different category indices and counts. Ranked compound information is now looked up from the current results rather than old hard-coded positions.

Source references use zero-based original cell indices. The notebook metadata and [provenance file](../results/provenance.json) record the source assessment, original notebook hashes, and extraction details. CSV files include their evidence references. Ranking values are raw saved counts; the complete posterior data and a verified denominator are unavailable.

Notebook format, Python 3.12 code syntax, recorded numeric evidence, local links, and the report's rendered layout were checked. The full analysis was not rerun because the TSV inputs are missing; a fresh dependency installation was also not verified. Interactive browser behavior was not verified; the graph data, JavaScript syntax, and local resources were checked.

## Rebuild figures and the PDF

The figure and PDF builders use files already included in the repository:

```bash
python scripts/build_visuals.py
python -m pip install -r requirements-presentation.txt
python scripts/build_report.py
```

The figure builder uses matplotlib and NumPy. It regenerates the PNG/SVG figures and local graph pages from the CSV and graph JSON exports. The PDF builder uses ReportLab and `report.md`. Neither reruns the analysis. The interactive gallery can also be opened directly at `visualizations/index.html`, without a server.

## Optional historical notebook rebuild

The combined notebook is already included. The optional editorial builder recreates it from the two private original assessment notebooks using Python 3.12 and `nbformat`, supplied through the Jupyter dependencies. When those source folders are beside the repository, run:

```bash
python scripts/build_notebook.py
```

Otherwise provide the source root or individual notebook paths:

```bash
python scripts/build_notebook.py --source-root /path/to/private/project
python scripts/build_notebook.py --assessment-one /path/to/first.ipynb --assessment-two /path/to/second.ipynb
```

This builder rewrites the combined notebook, checks its format and syntax, and verifies copied outputs against their source records. Executing the combined notebook with the TSV files does not require the private assessment folders.

`MANIFEST.json` records the delivered file sizes and SHA-256 hashes, excluding itself.

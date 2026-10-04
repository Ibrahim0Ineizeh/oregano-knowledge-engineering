# Setup and reproducibility

## Read without running

The report, CSV tables, PNG/SVG figures, and interactive graph gallery are included. Open `visualizations/index.html` in a browser after downloading the repository. The gallery's JavaScript and CSS are local vendor assets.

## Analysis environment

Use Python 3.12 with the pinned packages in `requirements.txt`. Versions were taken from the original second-stage Conda export. This is a concise pip package specification; the original files named “requirements.txt” were platform-specific Conda exports for macOS ARM64.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab notebooks/oregano-study.ipynb
```

The notebook imports PyMC and PyTensor for the probabilistic stage, Owlready2 for the ontology and queries, pandas/NumPy for tables, PyVis for graphs, and ArviZ/matplotlib for diagnostics. The dependencies and full analysis have not been installed and executed in a fresh environment for this archival edition.

## Required data

Place these files directly under `data/`:

```text
ACTIVITY.tsv       COMPOUND.tsv       DISEASES.tsv
EFFECT.tsv         GENES.tsv          INDICATION.tsv
PATHWAYS.tsv       PHENOTYPES.tsv     SIDE_EFFECT.tsv
TARGET.tsv         OREGANO_V2.1.tsv
```

Use the original assessment's OREGANO V2.1 input distribution for the closest comparison. A newer upstream version can have different identifiers, columns, and results. No source TSV files are included in this package or present in the workspace used to prepare it. See `data/README.md` for the upstream source.

Run the notebook sequentially. Stage 1 constructs `data/oregano.owl`; Stage 2 loads that file. The legacy ontology was 859,587,003 bytes (approximately 820 MiB) and is excluded from Git. It remains in the original local assessment folders.

## Compute requirements

The ontology, graph tables, sampling traces, and probability tensors all consume memory. The largest saved tensor alone was 807.13584 MB; allow several GB of available memory. Five sampling calls each request 1,000,000 draws per chain and 10,000 tuning iterations. Their saved logs reported four chains. Run time depends on the machine and environment; the historical logs do not provide a fresh performance guarantee.

## Historical outputs versus fresh results

The public notebook combines code and **saved outputs from the original runs**. It has not been rerun with the missing TSV inputs. Output metadata records the source assessment and original zero-based cell index.

Portability and identity fixes include path configuration, deterministic entity ordering, dynamic lookup of ranked compounds, and self-contained newly generated PyVis resources. These fixes can change category positions and sampled counts. Treat a fresh run as a new run; do not expect the retained historical category indices to map to its sorted entities. Do not interpret the saved counts as calibrated treatment probabilities.

The original saved execution counts were nonsequential, and the full posterior data were not retained. This edition checked notebook structure and syntax, extracted tables, reconciled identifiers, verified local artifact links, and visually reviewed the generated report. It does not certify clean execution of the original analysis.

## Rebuild presentation artifacts

```bash
python scripts/build_visuals.py
python scripts/build_report.py
```

The PDF builder requires `reportlab` (listed in `requirements-presentation.txt`); figure generation requires matplotlib and NumPy from the analysis requirements. The visual build script documents any optional access to original assessment files. Presentation rebuilds do not rerun the biomedical analysis.

The notebook build script is an editorial utility that reads the locally preserved original assessment notebooks. Those private source folders are intentionally outside the public package; the combined notebook itself is already included and does not require them to run with the source TSV files.

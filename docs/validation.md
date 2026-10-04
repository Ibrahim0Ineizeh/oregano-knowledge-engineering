# Publication validation

Checks completed on 4 October 2026:

- Combined notebook passed notebook-format validation. All 110 code cells and its build script parsed and compiled with Python 3.12.
- Historical outputs in copied cells matched the original source records. The notebook preserves 98 original output objects and records source cell indices and notebook hashes.
- Entity and relation totals, candidate-pool arithmetic, three indication-matched paths, Bayesian dimensions, and all fifteen ranking counts were checked against saved evidence.
- The five disease labels were reconciled with actual observed UMLS identifiers and NCBI MedGen records. The `DISEASE_160` ranking order was corrected using identifiers.
- Eight interactive graph pages have local asset references, consistent exported graph data, and valid edge endpoints. JavaScript syntax checks passed.
- Markdown and notebook artifact links resolve. The PDF has twelve pages, consistent numbering, working external reference annotations, and a gallery link relative to the PDF's location.
- Every final PDF page was rendered and visually inspected. Tables, headings, figures, and captions were checked for clipping and awkward table splits.
- The two credential values found in the original Graphistry experiment were checked against release files without displaying the values. Neither was copied.
- Source TSV files, oversized OWL files, assessment briefs, checkpoints, and the experimental Graphistry notebook are absent from the release.

The full biomedical analysis and a fresh dependency installation were **not** executed because the original TSV inputs are missing. Historical traces do not certify convergence. Interactive browser behavior was not verified because no computer-use browser was available; structural graph and resource checks were completed. The publication distinguishes those limits from the checks listed above.

`MANIFEST.json` records the SHA-256 and size of each delivered file, excluding itself. The ZIP includes the manifest and the publication folder only.

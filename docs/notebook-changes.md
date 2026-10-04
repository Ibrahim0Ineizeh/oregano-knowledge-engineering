# Notes on the combined notebook

The [combined notebook](../notebooks/oregano-study.ipynb) brings the ontology construction and exploration from the first assessment together with the indirect-path search and Bayesian model from the second. It can be read independently, with the accompanying [report](../report.md) providing the presentation figures and findings.

All stored outputs are copied from the original assessment notebooks. They have **not been regenerated after the changes below**. Original execution counts are retained, including their nonsequential order. The public edition does not certify a clean execution or the convergence of the historical chains.

## Editorial organization

- A shared title, overview and setup lead into Stage 1 and Stage 2.
- Assignment question numbers, course covers, the student identifier and rerun reminders have been removed. Ibrahim Ineizeh's name and direct, first-person explanation are retained.
- Explanations have been edited for grammar and qualified to distinguish asserted graph links, heuristic model assumptions and clinical evidence.
- AI use in the original work remains disclosed. The 2026 editorial and packaging assistance is disclosed separately.
- Original references remain as background reading, with no claim that they validate the probability weights.
- Static publication figures are linked beside the workflow, graph counts, candidate paths and Bayesian explanation. They make the findings readable even when a notebook viewer cannot display the historical HTML frames.

## Portable code and historical provenance

- `ROOT`, `DATA_DIR`, `OWL_PATH` and `OUTPUT_DIR` resolve from the package root or its `notebooks` directory. Input tables are read from `data/`; the ontology is saved to `data/oregano.owl`; generated HTML files are written to `visualizations/generated/`.
- Missing input tables or a missing ontology raise a `FileNotFoundError` that names the required files or next step.
- Each construction/loading stage uses an isolated Owlready2 `World`, and queries use that world. This avoids mixing a graph with data left in a previous session.
- PyVis graphs use inline resources and a shared save/display helper. Historical iframe outputs remain historical records; GitHub may not display those frames. The report and presentation assets provide readable result views.
- The original fixed numerical seed is kept as `SEED = 40490625` for continuity with the recorded analysis.
- Bayesian entity lists are deduplicated and sorted by IRI. Original category indices came from unordered sets and should not be reused as identifiers in a new run.
- Compound information is printed from `counts.index[:3]` instead of hard-coded category numbers. The original information call for `DISEASE_160` reversed ranks two and three.
- The neighborhood helper now defines its deduplicated result for a one-step neighborhood as well as larger neighborhoods. Graph edges are sorted for stable display.
- A construction variable formerly named `range` has been renamed so that it cannot shadow the `range()` function used in Stage 2.
- Nested f-string quotes have been normalized. Every code cell is parsed and compiled during the notebook build; this checks syntax without running the analysis.
- Copied cells record `assessment-1` or `assessment-2`, their zero-based original cell index and source-notebook SHA-256 in metadata. Code metadata also marks outputs as retained and unregenerated. The shared setup records its derivation from both original import cells.

The substantive construction, query, path-filtering, probability-table and sampling methods are retained. The one-million-draw requests are expensive and remain visible in the code. No original analysis was executed during packaging because the required TSV input tables were absent.

## Identifier and interpretation corrections

The original second assessment used Gemini to interpret biomedical identifiers. Four disease labels did not match the observed ontology records. The public notebook now labels the experiments by their stored identifiers:

| Ontology record | Original heading | Corrected heading | Stored UMLS field |
|---|---|---|---|
| `DISEASE_13735` | Adult T-cell Leukemia-Lymphoma | [Type 2 diabetes](https://www.ncbi.nlm.nih.gov/medgen/41523) | `C0011860;C1852091;C4017238` |
| `DISEASE_13720` | Colorectal cancer | [Colorectal cancer](https://www.ncbi.nlm.nih.gov/medgen/3170) | `C0007102;C0009402` |
| `DISEASE_2810` | Sarcoidosis | [Retinitis pigmentosa](https://www.ncbi.nlm.nih.gov/medgen/20551) | `C0035334` |
| `DISEASE_160` | Aortic stenosis | [Amyotrophic lateral sclerosis](https://www.ncbi.nlm.nih.gov/medgen/274) | `C0002736` |
| `DISEASE_7426` | COPD | [Breast cancer](https://www.ncbi.nlm.nih.gov/medgen/651) | `C0346153;C0006142;C1861906` |

The linked NCBI MedGen records were checked on 4 October 2026. Some graph records contain several UMLS codes; the displayed label reflects the checked representative concept, while the OREGANO ID remains the primary experiment identifier. Correcting a heading does not rerun the corresponding experiment. Unverified drug identities guessed for unnamed NPASS records have been removed. The retained counts are outcomes of the graph model, not treatment recommendations, validated efficacy measurements or posterior probabilities of clinical success.

The indirect-path pool contains 9,449 compounds; the direct-treatment set contains 435, with 215 in their intersection. Removing that intersection leaves 9,234 compounds. The three indication-matched paths can reveal missing treatment triples, but their existing indication information does not establish a newly discovered clinical use.

## Logical and modeling qualifications

The all-molecule coverage statement uses `∀m ∃c`: each molecule has some linked compound. It does not use `∃c ∀m`, which would claim that one compound links to every molecule. Equivalent quantifier corrections are made for full activity, effect and pathway coverage. Partial coverage is described with existential statements. The saved coverage query uses `SELECT ?node` without `DISTINCT`; the retained numbers have not been certified as distinct-node counts and need a follow-up audit.

The original `has_target` property can declare both molecule and protein ranges. Multiple OWL range declarations imply their intersection. The public code retains this historical construction, but the schema needs reasoner validation and an appropriate union or common superclass before logical entailments are claimed. Multiple data-property domains also need a schema audit. Neither missing-link checks nor visual inspection establish OWL consistency.

The Bayesian variables are categorical entity identities. The compound prior is uniform. The gene table uses manually chosen group masses 0.50, 0.30, 0.15 and 0.05. The protein table adds a 50/50 targeted/untargeted distribution to a 40/60 gene-encoded/other distribution, then normalizes. The disease table counts connected gene–disease links and normalizes them. These are heuristic weights, not experimentally measured probabilities or a validated biomedical causal model.

Disease selection uses row sums of `P(D | P)`, not the network's marginal disease probability. The selected-compound threshold favors highly connected records. Full posterior samples, verified percentage denominators, numerical convergence diagnostics and a formal sensitivity analysis were not retained. The stored trace plots should therefore be read with those limits.

## Optional historical rebuild

The public notebook itself needs only the declared Python dependencies and original OREGANO data to execute. It does **not** require the original assessment folders.

The optional `scripts/build_notebook.py` publishing tool recreates this editorial merge from the private original notebooks. It requires `nbformat` and a Python 3.12 environment. When the private source folders are beside the public package, run:

```sh
python scripts/build_notebook.py
```

Otherwise provide the private source root or individual notebook paths:

```sh
python scripts/build_notebook.py --source-root /path/to/private/project
python scripts/build_notebook.py --assessment-one /path/to/first.ipynb --assessment-two /path/to/second.ipynb
```

The builder validates notebook format, compiles every code cell without executing it, and checks that copied outputs match their original records. It rewrites only the combined notebook. The credential-containing experimental Graphistry notebook, checkpoints and local IDE files are not part of the merge.

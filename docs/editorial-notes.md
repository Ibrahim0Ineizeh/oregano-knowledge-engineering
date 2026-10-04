# Editorial notes and evidence

This edition joins two stages of one project and preserves their recorded outputs. The original assessment folders remain unchanged outside `public-release/`. Course briefs, downloaded papers, duplicate ontology files, notebook checkpoints, operating-system files, and the credential-containing Graphistry experiment are excluded.

## Changes to the account

| Original issue | Treatment in the combined edition |
| --- | --- |
| Separate assessment question structure | Continuous research account: construction, exploration, path search, model, results, reflection. |
| Four disease headings disagree with observed UMLS codes | Labels corrected using the saved OWL identifiers and NCBI MedGen; original labels retained in a correction table. |
| Guessed names for unnamed NPASS records | Saved identifiers retained; guessed identities and associated treatment claims omitted. |
| `DISEASE_160` information display reverses ranks 2 and 3 | Rankings reconciled by saved category index, NPASS record, and OWL compound ID. |
| All direct-treatment compounds subtracted from path count | Correct overlap is 215: 9,449 minus 215 equals 9,234. |
| “Full graph” filename | Relabeled as a 1,500-edge general sample. |
| Coverage interpreted as one entity connecting to every other entity | Quantifier order corrected to “each destination has some source.” |
| Sampled missing edges interpreted as biological absence | Conclusions limited to recorded and displayed relationships. |
| Hand-set weights described as measured biological probabilities | Described as heuristics with their exact implementation. |
| Summed disease conditional rows called a marginal distribution | Described as a disease selection score. |

## Unresolved methodological limits

- Multiple OWL property ranges/domains express intersections; the original intended alternatives are not reasoner-validated.
- Some participation queries omit `DISTINCT`; retained coverage outputs need an explicit distinct-node audit.
- Missing attributes are encoded as zero; semicolon-separated identifiers are not robustly reconciled by first-value equality.
- High-degree selection and manually assigned weights introduce biases.
- Full posterior samples, numerical convergence diagnostics, predictive evaluation, and clinical validation are unavailable.
- Stored notebook outputs are historical, with nonsequential execution counts. The full pipeline has not been rerun for this edition.

## Source provenance

All source notebook cell references are zero-based. The canonical second-stage source was the submitted notebook, which was byte-for-byte identical to its working copy. Source SHA-256 values:

```text
Assessment 1: a47267999ed5f48e83c830269ba0ed34c13e3f959c84d9b47a865bd3988ff23b
Assessment 2: 1a90a8b74740c63d95e05f6a1d9006536713ad09412b65e96036cbd6d4362d72
```

Per-cell provenance is stored in the combined notebook; result tables include evidence references. Source hashes and further extraction details are in `results/provenance.json`. No Git history is invented for the assessment work: the process is reconstructed from saved notebooks and artifacts.

The three additional arsenic-trioxide paths were checked directly in named-individual records of the saved OWL file. The five ranking disease labels were checked against NCBI MedGen on 4 October 2026. These checks establish the cited identifiers and paths, not treatment efficacy.

## Publication hygiene

The experimental Graphistry notebook and its checkpoint contain embedded credentials. They were not copied into the publication folder or its ZIP. The author should revoke those credentials before sharing any original folders or history that might contain them. Only the contents of `public-release/` are intended for upload.

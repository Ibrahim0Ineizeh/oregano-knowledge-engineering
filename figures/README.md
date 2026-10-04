# Publication figures

Each figure is supplied as a PNG for direct viewing and an editable SVG for
publication. The figures use the recorded tables in `../results/`; source cell
references are printed on the figures and recorded in the result exports.

| Figure | Content |
| --- | --- |
| `workflow` | Six stages across the two assessments |
| `graph_composition` | Entity and relation counts on explicitly labeled logarithmic axes |
| `candidate_paths` | Three compound–protein–gene–disease paths with matching indication codes |
| `trioxide_paths` | Three additional graph-connected arsenic trioxide candidate branches |
| `bayesian_network` | Implemented model arrows and joint-probability factorization |
| `posterior_rankings` | Five panels of raw saved top-three compound counts |

Regenerate all figures and offline graph pages from the release directory:

```sh
python scripts/build_visuals.py
```

This requires Matplotlib and its NumPy dependency. It does not execute the original
notebooks, download biomedical data, or rerun Bayesian sampling.

#!/usr/bin/env python3
"""Rebuild the editorial notebook from private historical assessment notebooks.

This optional publishing tool does not execute the analysis. The public notebook
already contains the merged study and does not require the historical sources.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import textwrap


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = {
    "assessment-1": Path("Assessment 1/ke-project/code"),
    "assessment-2": Path("Assessment 2/submission"),
}


def clean(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


INTRO = clean(r"""
    # OREGANO: From ontology construction to Bayesian candidate ranking

    **Ibrahim Ineizeh**

    Combined knowledge engineering study · original analysis: 2025 · editorial packaging: 2026

    I first built an ontology from OREGANO and explored how its entities connect. I then used those connections to search for missing treatment links and construct a Bayesian model for ranking compounds against selected disease nodes. This notebook brings both stages together so that the construction, decisions, findings and limitations can be read in one sequence.

    **Reading the results.** Every stored code output below comes from the original assessment notebooks. I have retained those outputs as a historical record; they have **not been regenerated after the portability, ordering and display changes**. Original category indices and execution counts therefore describe the saved run. A new run can produce different indices and rankings. The sampled counts are model outputs, not probabilities that a drug will treat a disease.

    The accompanying [report](../report.md) presents the findings and figures. [Setup and reproducibility](../docs/reproducibility.md) explains how to run or rebuild the study and the limits of reproduction.

    **Contents**

    - Setup and data paths
    - Stage 1: Constructing and exploring the ontology
    - Stage 2: Indirect paths and Bayesian candidate ranking
    - Reflections, AI disclosure and references

    ![Workflow from ontology construction to candidate inspection](../figures/workflow.png)
""")

SETUP_NOTE = clean(r"""
    ## Setup and data paths

    I use the package root as the working reference, so the notebook can run from the root directory or its `notebooks` directory. Place the original OREGANO entity tables and `OREGANO_V2.1.tsv` in `data/`, as described in the package documentation. The construction stage writes `data/oregano.owl`; generated HTML graphs go to `visualizations/generated/`.

    This is the full original analysis, including large arrays and long sampling runs. The protein conditional tensor alone occupied about 807 MB in the saved run. Each disease sampling call requests one million draws per chain. Reading the retained tables and plots does not require running the notebook.
""")

CONFIG = clean(r"""
    from pathlib import Path

    _working_dir = Path.cwd().resolve()
    ROOT = next(
        (
            candidate
            for candidate in (_working_dir, _working_dir.parent)
            if (candidate / "notebooks" / "oregano-study.ipynb").is_file()
            and (candidate / "scripts").is_dir()
        ),
        None,
    )
    if ROOT is None:
        raise FileNotFoundError(
            "Cannot locate the study package. Open this notebook from the package "
            "root or its notebooks directory."
        )

    DATA_DIR = ROOT / "data"
    OWL_PATH = DATA_DIR / "oregano.owl"
    OUTPUT_DIR = ROOT / "visualizations" / "generated"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Historical fixed seed; retained to explain the original runs.
    SEED = 40490625

    from owlready2 import *
    import pandas as pd
    import numpy as np
    from pyvis.network import Network
    from tqdm.notebook import tqdm
    import pymc as mc
    import pytensor.tensor as pt
    import arviz as az
    import matplotlib.pyplot as plt
    from IPython.display import HTML
    import random

    # An isolated world avoids mixing this study with a previous notebook run.
    world = World()

    def show_graph(network, filename):
        # Save a portable HTML graph and display its embedded resources.
        output_path = OUTPUT_DIR / filename
        network.write_html(str(output_path), notebook=True, open_browser=False)
        return HTML(filename=str(output_path))
""")

A1_MARKDOWN = {
    2: "## Stage 1: Constructing and exploring the ontology",
    3: """Drug repurposing investigates whether an existing compound has useful connections to another disease. I used OREGANO, a knowledge graph developed for computational drug repurposing [1], to explore those connections. I first converted the tabular entities and relations into an OWL ontology, then used queries and visualizations to inspect its structure.""",
    4: """The original target table contains both proteins and molecules. I separated these into two entity classes because their connections differ. I also kept `has_code` as compound information rather than an object relation, since it does not link two entity records in these input tables.""",
    5: "### Loading the tables and constructing the ontology",
    6: """I normalized column names and entity identifiers so they could be used in the OWL file. Missing table values were stored as zero in the original implementation. That convention is retained here and should be treated as missing information, rather than a measured biological value.""",
    19: "I saved the constructed ontology so the same asserted graph could be loaded for exploration and the second stage.",
    21: "### Exploring the graph structure",
    22: "I loaded the saved ontology into a fresh world before querying it. This makes each exploration stage independent of objects left in the construction session.",
    24: "#### Relation types and counts",
    25: """I retrieved the object properties, queried the triples using each relation and displayed the counts in a dataframe. The saved ontology has **17 relation types**. These are asserted graph links; their counts do not measure the strength of a biological effect.""",
    29: "#### Entity types and counts",
    30: """I then listed the ontology classes and counted the records belonging to each class. Splitting `TARGET` into `MOLECULE` and `PROTEIN` gives **11 entity types** in the saved output. The protein records connect to genes through `gene_product_of`, whereas the molecule records do not have that relation in this graph.

![Graph composition from the historical outputs](../figures/graph_composition.png)""",
    34: "#### Coverage across relation types",
    35: """I wanted to see which entity types participate in each relation, either as a source or a destination. The saved coverage table helped guide the logical descriptions below. The retained query uses `SELECT ?node`, without `DISTINCT`, so it may count repeated matches. I have not recomputed or certified these saved numbers as unique-node counts; a follow-up coverage audit should explicitly count distinct identifiers.""",
    37: "#### Visualizing the ontology",
    38: """I used the class names, record counts and relation counts to build a schema graph with PyVis. This view makes the different roles of proteins and molecules easier to inspect.

The original object-property construction can assign several range classes to one property, including `MOLECULE` and `PROTEIN` for `has_target`. In OWL, multiple range declarations mean an intersection, not a choice between classes. I preserve that original construction here to document the analysis, but the schema has not been validated with a reasoner. A revised schema should use an appropriate union or common superclass before making logical entailment claims.""",
    42: """The graph shows why I separated proteins and molecules: their asserted links to genes differ. The two compound-efficacy relations also overlap visually in this schema view. The visual is an overview of the original asserted structure; it does not resolve the range-modeling limitation described above.""",
    43: "#### Logical descriptions and coverage checks",
    44: r"""The saved output records 90,868 compounds, with 61,171 lacking a `has_target` link, and no molecules lacking an incoming target link. The intended statement about molecule coverage is **each molecule has at least one connected compound**. It does not say that a single compound targets every molecule.

I use the corresponding quantifier order, $\forall m\,\exists c$, below. The `FILTER NOT EXISTS` checks inspect missing asserted links in this dataset. They do not establish biological absence under OWL's open-world interpretation, and they are not a proof that the ontology is consistent.""",
    48: r"""**Molecule coverage**

$$\forall m\,[\mathrm{Molecule}(m)\Rightarrow\exists c\,(\mathrm{Compound}(c)\land\mathrm{has\_target}(c,m))].$$""",
    50: r"""**Observed compound–protein links**

$$\exists c\,\exists p\,[\mathrm{Compound}(c)\land\mathrm{Protein}(p)\land\mathrm{has\_target}(c,p)].$$""",
    52: r"""**Activity coverage**

$$\forall a\,[\mathrm{Activity}(a)\Rightarrow\exists c\,(\mathrm{Compound}(c)\land\mathrm{has\_activity}(c,a))].$$""",
    54: r"""**Observed increases in activity**

$$\exists c\,\exists a\,[\mathrm{Compound}(c)\land\mathrm{Activity}(a)\land\mathrm{increase\_activity}(c,a)].$$""",
    56: r"""**Observed decreases in activity**

$$\exists c\,\exists a\,[\mathrm{Compound}(c)\land\mathrm{Activity}(a)\land\mathrm{decrease\_activity}(c,a)].$$""",
    58: r"""**Observed indications**

$$\exists c\,\exists i\,[\mathrm{Compound}(c)\land\mathrm{Indication}(i)\land\mathrm{has\_indication}(c,i)].$$""",
    60: r"""**Observed side-effect links**

$$\exists c\,\exists s\,[\mathrm{Compound}(c)\land\mathrm{SideEffect}(s)\land\mathrm{has\_side\_effect}(c,s)].$$""",
    62: r"""**Effect coverage**

$$\forall e\,[\mathrm{Effect}(e)\Rightarrow\exists c\,(\mathrm{Compound}(c)\land\mathrm{has\_effect}(c,e))].$$""",
    64: r"""**Observed increases in effect**

$$\exists c\,\exists e\,[\mathrm{Compound}(c)\land\mathrm{Effect}(e)\land\mathrm{increase\_effect}(c,e)].$$""",
    66: r"""**Observed decreases in effect**

$$\exists c\,\exists e\,[\mathrm{Compound}(c)\land\mathrm{Effect}(e)\land\mathrm{decrease\_effect}(c,e)].$$""",
    68: r"""**Observed treatment links**

$$\exists c\,\exists d\,[\mathrm{Compound}(c)\land\mathrm{Disease}(d)\land\mathrm{is\_substance\_that\_treats}(c,d)].$$""",
    70: r"""**Observed compound–gene links**

$$\exists c\,\exists g\,[\mathrm{Compound}(c)\land\mathrm{Gene}(g)\land\mathrm{is\_affecting}(c,g)].$$""",
    72: r"""**Observed protein–gene links**

$$\exists p\,\exists g\,[\mathrm{Protein}(p)\land\mathrm{Gene}(g)\land\mathrm{gene\_product\_of}(p,g)].$$""",
    74: r"""**Pathway coverage**

$$\forall t\,[\mathrm{Pathway}(t)\Rightarrow\exists g\,(\mathrm{Gene}(g)\land\mathrm{acts\_within}(g,t))].$$""",
    76: r"""**Observed gene–disease links**

$$\exists g\,\exists d\,[\mathrm{Gene}(g)\land\mathrm{Disease}(d)\land\mathrm{causes\_condition}(g,d)].$$""",
    78: r"""**Observed disease–phenotype links**

$$\exists d\,\exists o\,[\mathrm{Disease}(d)\land\mathrm{Phenotype}(o)\land\mathrm{has\_phenotype}(d,o)].$$""",
    80: r"""**Observed increases in compound efficacy**

$$\exists c_1\,\exists c_2\,[\mathrm{Compound}(c_1)\land\mathrm{Compound}(c_2)\land\mathrm{increase\_efficacy}(c_1,c_2)].$$""",
    82: r"""**Observed decreases in compound efficacy**

$$\exists c_1\,\exists c_2\,[\mathrm{Compound}(c_1)\land\mathrm{Compound}(c_2)\land\mathrm{decrease\_efficacy}(c_1,c_2)].$$""",
    83: "#### Inspecting a sampled knowledge graph",
    84: """I created query-based lists of nodes and edges, then sampled relation rows with a fixed seed to keep the graph readable. The helper can focus on a chosen set of relations or use every available relation. Sampling is with replacement, so this display is an inspection view rather than a representative graph statistic.""",
    85: """I included the available compound names, DrugBank effect/activity descriptions and indication/side-effect names in node tooltips. Missing descriptions remain missing; I did not infer an identity from an unlabeled node.""",
    90: "I assigned colors to the entity types and emphasized increasing and decreasing efficacy with different edge colors.",
    94: """The original sampled graph contained compound-efficacy chains and connections between compounds, genes and disease nodes. Those paths motivated the second stage: I wanted to inspect indirect associations that were not represented by an explicit treatment edge. The sample alone does not show that a compound is ineffective, safe or a treatment. I treat the biomedical interpretations in the original assessment as exploratory observations that need a separate evidence check.""",
}

A2_MARKDOWN = {
    0: "## Stage 2: Indirect paths and Bayesian candidate ranking",
    2: "### Loading the ontology for the second stage",
    4: "#### Reviewing the ontology structure",
    11: "### Helpers for querying and visualizing neighborhoods",
    12: "#### Query helpers",
    17: "#### Visualization helpers",
    22: "### Searching for indirect compound–disease paths",
    23: """I searched backward from disease records, following `causes_condition` to genes, `gene_product_of` to proteins and `has_target` to compounds. This gives the graph path:

**Compound → Protein → Gene → Disease**

I then removed compounds with any explicit `is_substance_that_treats` link in the graph. This exclusion applies across all disease nodes, rather than only to an individual compound–disease pair.""",
    25: "I queried the direct treatment links separately so that I could remove their intersection with the indirect-path compound set.",
    29: """The saved outputs contain 9,449 compounds in the indirect-path set and 435 compounds with a direct treatment link. Only 215 belong to both sets, leaving **9,234** after the exclusion.

To trim the remaining paths, I required a nonzero compound name, disease MESH and UMLS information, and an exact match between the disease's first UMLS field and an indication's first SIDER field. I also required the gene to have a disease link. This original exact-field comparison does not split lists of identifiers stored in one string.

An indication match is evidence that the dataset already contains relevant indication information. Recovering that match can reveal a missing explicit treatment triple; it does not establish a new clinical use.""",
    31: """The saved table contains three matching paths: Arsenic trioxide, Desmopressin and Mifepristone, with their proteins, genes, diseases and indication identifiers. I used neighborhood graphs to inspect the path context. The matching rows are graph findings, not independent clinical validation.

![The three identifier-matched compound–disease paths](../figures/candidate_paths.png)""",
    35: """I highlighted **Arsenic trioxide (`COMPOUND_1149`)**. The graph links it to `PROTEIN_1617`, then `GENE_31050`, then `DISEASE_1831`. The disease's UMLS code and the compound indication's SIDER code both equal `C0023487`, with the saved indication title *Acute Promyelocytic Leukemia*.

The saved neighborhood also contains paths to `DISEASE_17027` and `DISEASE_17128` through `PROTEIN_916` and `GENE_29198`, and to `DISEASE_3387` through `PROTEIN_1503` and `GENE_32278`. These additional connections are hypotheses for inspection. A connected path alone does not demonstrate treatment efficacy.

![Additional arsenic-trioxide paths checked in the retained ontology](../figures/trioxide_paths.png)""",
    36: "### Constructing the Bayesian network",
    37: """I used compound, gene, protein and disease records as categorical variables. Each variable identifies one entity from the selected graph subset. The model therefore ranks **entity identities under graph-derived weights**; it does not represent binary gene activity, protein misfolding or a measured treatment response.

I chose the dependencies `C → G`, `C → P`, `G → P` and `P → D`. They summarize the graph connections used in this experiment. The `P → D` dependency is constructed through protein–gene and gene–disease links. I regard this structure as an exploratory modeling assumption, rather than a verified biomedical causal graph.""",
    39: r"""The joint distribution follows the dependencies I selected:

$$P(C,G,P,D)=P(C)\,P(G\mid C)\,P(P\mid G,C)\,P(D\mid P).$$

Here, $C$, $G$, $P$ and $D$ are compound, gene, protein and disease **identities**. The conditional tables below translate asserted links into normalized heuristic weights.

![The dependencies and factorization of the categorical Bayesian model](../figures/bayesian_network.png)""",
    40: """### Building the conditional probability tables

The full graph would require very large arrays. From the **9,234 remaining path-connected compounds**, I therefore kept those with **more than 200** combined protein-target and direct gene links, then collected their proteins, genes and connected diseases. The saved subset contains **60 compounds, 2,009 proteins, 837 genes and 1,190 diseases**.

The public code sorts each deduplicated entity list by IRI. The original code used unordered sets, so the retained outputs use historical category indices that can differ from a new run.""",
    43: r"""I assigned a uniform compound prior, $P(C=c)=1/60$, so no selected compound was preferred before conditioning on the other variables.""",
    45: r"""For $P(G\mid C)$, I separated genes into four groups:

1. Directly affected genes whose encoded proteins are targeted by the compound.
2. Directly affected genes whose encoded proteins are not targeted.
3. Other genes whose encoded proteins are targeted.
4. Other genes whose encoded proteins are not targeted.

I gave these groups masses **0.50, 0.30, 0.15 and 0.05** respectively. I renormalized over nonempty groups and distributed each group's mass equally among its genes. If the compound had no directly affected genes, I used a uniform distribution. These values are choices in the model, not probabilities estimated from experiments.""",
    47: r"""For $P(P\mid G,C)$, I added two distributions and normalized each conditional column:

- The compound component splits mass **50/50** between targeted and untargeted proteins, uniformly within each group.
- The gene component splits mass **40/60** between proteins encoded by the gene and other proteins, uniformly within each group.

An empty target or encoded-protein group uses the original uniform fallback. When both components sum to one, normalization produces their equal mixture. The original discussion of binding concentrations and protein heritability did not establish these weights as biological probabilities; I retain them as heuristic assumptions.""",
    49: r"""For $P(D\mid P)$, I counted each disease link of a protein's associated genes, then normalized the resulting disease weights for that protein. A gene with no disease link contributes a uniform distribution; a protein with no associated genes also receives a uniform distribution.

In the original process, I tried weights of 0.8, 0.9 and 1 for linked diseases and selected 1 because the outputs appeared more consistent. I did not retain a formal sensitivity analysis or external validation for that choice. It is not evidence that a protein causes a disease with certainty.""",
    52: """### Conditioning on selected diseases

I selected six disease nodes by summing each row of `P(D | P)`, then excluded `DISEASE_11304` because its UMLS and MESH fields were missing. This row-sum score does **not** equal the network's marginal disease probability, since it omits the upstream distributions.

For each remaining node, I fixed its category as observed evidence and sampled the other categorical variables. I then counted the compound categories in the saved posterior table and printed the three largest counts. The original logs report four chains and 4,040,000 draws, while the calls request 1,000,000 draws and 10,000 tuning iterations per chain. The full posterior samples are not included, so I report raw counts without a verified posterior-percentage denominator.

**Identifier correction.** The original assessment used Gemini to interpret disease and compound identifiers. Four disease headings were incorrect. The sections below now follow the stored ontology identifiers: type 2 diabetes, colorectal cancer, retinitis pigmentosa, amyotrophic lateral sclerosis and breast cancer. NCBI MedGen records support the representative labels, with source links in the references. Nodes containing multiple UMLS codes remain identified primarily by their OREGANO IDs. This corrects the labels attached to the saved experiments; the sampling has not been rerun. Unverified names guessed for unlabeled NPASS compounds have been removed.

![Saved top-three compound counts for each observed disease node](../figures/posterior_rankings.png)""",
    53: "#### Type 2 diabetes — `DISEASE_13735`",
    62: """The saved top counts identify Resveratrol (`NPC161571`), Genistein (`NPC39426`) and Quercetin (`NPC20791`). They were sampled against `DISEASE_13735`, whose stored UMLS field is `C0011860;C1852091;C4017238`. The original Adult T-cell Leukemia-Lymphoma heading was incorrect.

I treat these counts as outcomes of the specified graph model. Their interpretation needs identifier validation, reproducible category ordering and independent evidence; the saved ranking does not establish treatment for type 2 diabetes.""",
    63: "#### Colorectal cancer — `DISEASE_13720`",
    69: """The saved top categories correspond to `NPC136002`, `NPC482689` and `NPC480173`. Their displayed compound-name fields are missing, so I retain their identifiers rather than the drug names guessed in the original discussion. The observed disease field is `C0007102;C0009402`. The ranking is an exploratory model result and does not establish an approved or effective treatment.""",
    70: "#### Retinitis pigmentosa — `DISEASE_2810`",
    76: """The saved top categories correspond to Resveratrol (`NPC161571`), `NPC109083` and `NPC482689`. The observed disease code is `C0035334`; the original Sarcoidosis heading was incorrect. I keep unnamed compounds as identifiers and make no clinical conclusion from their presence in the ranking.""",
    77: "#### Amyotrophic lateral sclerosis — `DISEASE_160`",
    83: """The saved ranked category order is `5`, `51`, `39`: `NPC480173`, `NPC482689`, `NPC471579`. The original information-printing call used `5`, `39`, `51`, so it reversed the second and third records. The public code now prints information directly from the current ranked indices.

The disease's stored UMLS code is `C0002736`; the original Aortic Stenosis heading was incorrect. None of these unlabeled compound records is assigned a guessed drug identity here.""",
    84: "#### Breast cancer — `DISEASE_7426`",
    90: """The saved top categories correspond to Resveratrol (`NPC161571`), `NPC32373` and `NPC485883`. The observed disease's UMLS field is `C0346153;C0006142;C1861906`; the original COPD heading was incorrect. The ranking does not support the original disease-specific treatment discussion. I retain the counts as historical model results and leave the unnamed compounds unresolved.""",
}

REFLECTIONS = clean(r"""
    ## Reflections and limits of the study

    I learned that a graph can support several different questions: how the data is organized, where explicit links are missing, and how an assumed probability model ranks connected entities. The three identifier-matched paths provide a concrete graph-completeness finding. The Bayesian stage shows a modeling process, but its rankings depend on hand-set weights and on restricting the graph to high-degree compounds.

    I would next validate the OWL schema, audit distinct-node coverage, resolve compound and disease identifiers, compare weights in a sensitivity analysis, and report numerical convergence diagnostics. The saved trace plots alone are insufficient to verify convergence. Missing graph links should not be interpreted as biological absence, and candidate rankings require independent biomedical evaluation.

    ## AI disclosure

    In the original work, I used AI to help with SPARQL queries, grammar and vocabulary, and understanding biomedical concepts. In the second assessment, disease and compound interpretations were sourced using Gemini. The identifier audit found errors in those interpretations, which this public edition now identifies and corrects.

    In 2026, I used Codex for editorial packaging: combining the two notebooks, organizing the explanation, checking identifiers against the retained ontology and public references, creating presentation assets, and making paths and display code portable. The original analysis has not been rerun, and this assistance does not independently validate the model or its clinical interpretation.

    ## References and original background reading

    [1] Boudin, M., Diallo, G., Drancé, M. et al. (2023). *The OREGANO knowledge graph for computational drug repurposing*. Scientific Data, 10, 871. https://doi.org/10.1038/s41597-023-02757-0

    Disease identifier checks, performed on 4 October 2026:

    - NCBI MedGen. *Type 2 diabetes mellitus*, concept `C0011860`. https://www.ncbi.nlm.nih.gov/medgen/41523
    - NCBI MedGen. *Colorectal carcinoma*, concept `C0009402`. https://www.ncbi.nlm.nih.gov/medgen/3170
    - NCBI MedGen. *Retinitis pigmentosa*, concept `C0035334`. https://www.ncbi.nlm.nih.gov/medgen/20551
    - NCBI MedGen. *Amyotrophic lateral sclerosis*, concept `C0002736`. https://www.ncbi.nlm.nih.gov/medgen/274
    - NCBI MedGen. *Malignant tumor of breast*, concept `C0006142`. https://www.ncbi.nlm.nih.gov/medgen/651

    The following sources were included as background in the original second assessment. They do not validate the numerical weights used in this model, and the original biomedical interpretations should not be inferred from their inclusion.

    - Wikipedia contributors. *Proteinopathy*. https://en.wikipedia.org/wiki/Proteinopathy
    - Original assessment background link on proteinopathy and disease progression. https://www.mdpi.com/2079-9721/11/1/30
    - MedlinePlus Genetics. *How can gene variants affect health and development?* https://medlineplus.gov/genetics/understanding/mutationsanddisorders/mutationscausedisease/
    - Wikipedia contributors. *Active site*. https://en.wikipedia.org/wiki/Active_site
    - Drouard et al. (2025), original assessment background on protein heritability. https://doi.org/10.1021/acs.jproteome.4c00971
    - Encyclopaedia Britannica. *Mechanisms of mutation*. https://www.britannica.com/science/heredity-genetics/Mechanisms-of-mutation
""")


def cell(kind: str, source: str, identity: str) -> dict:
    result = {
        "cell_type": kind,
        "id": hashlib.sha256(identity.encode()).hexdigest()[:12],
        "metadata": {},
        "source": clean(source).splitlines(keepends=True),
    }
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def transform_code(assessment: str, index: int, source: str) -> str:
    source = source.replace("default_world.sparql", "world.sparql")
    source = source.replace("40490625", "SEED")
    source = source.replace("Network(directed=True, notebook=True)",
                            'Network(directed=True, notebook=True, cdn_resources="in_line")')
    source = source.replace("Network(directed=True)",
                            'Network(directed=True, notebook=True, cdn_resources="in_line")')
    if assessment == "assessment-1":
        source = source.replace('get_ontology("http://www.dummy.info/new.owl")',
                                'world.get_ontology("http://www.dummy.info/new.owl")')
        source = source.replace("open(f'../data/{entity}.tsv')",
                                'open(DATA_DIR / f"{entity}.tsv", encoding="utf-8")')
        source = source.replace("open('../data/OREGANO_V2.1.tsv')",
                                'open(DATA_DIR / "OREGANO_V2.1.tsv", encoding="utf-8")')
        source = source.replace("onto.save('oregano.owl')", 'onto.save(file=str(OWL_PATH))')
        if index == 8:
            guard = clean('''
                required_tables = [
                    "ACTIVITY", "COMPOUND", "DISEASES", "EFFECT", "GENES",
                    "INDICATION", "PATHWAYS", "PHENOTYPES", "SIDE_EFFECT", "TARGET",
                ]
                required_paths = [DATA_DIR / f"{name}.tsv" for name in required_tables]
                required_paths.append(DATA_DIR / "OREGANO_V2.1.tsv")
                missing_paths = [path for path in required_paths if not path.is_file()]
                if missing_paths:
                    raise FileNotFoundError(
                        "OREGANO input tables are missing: "
                        + ", ".join(str(path) for path in missing_paths)
                        + ". Place the original release tables in the package data directory."
                    )
                world = World()
            ''')
            source = guard + "\n" + source
        if index == 15:
            # A1's global variable called range would break A2's range() calls.
            source = source.replace("range = type(nodes", "target_type = type(nodes")
            source = source.replace("EntityClasses[range]", "EntityClasses[target_type]")
        if index == 23:
            source = ontology_load()
        if index == 41:
            source = source.replace('net.show("ontology.html")',
                                    'show_graph(net, "stage-1-ontology.html")')
        if index == 93:
            source = source.replace("f'{node['src_name']}/{node['src_info']}'",
                                    'f"{node[\'src_name\']}/{node[\'src_info\']}"')
            source = source.replace("f'{node['dest_name']}/{node['dest_info']}'",
                                    'f"{node[\'dest_name\']}/{node[\'dest_info\']}"')
            source = source.replace('net2.save_graph("knowledge_graph.html")',
                                    'show_graph(net2, "stage-1-knowledge-graph.html")')
            source = re.sub(r"^#net2\.save_graph.*\n?", "", source, flags=re.MULTILINE)
    else:
        if index == 3:
            source = ontology_load()
        if index == 10:
            source = source.replace('ont_net.show("ontology.html")',
                                    'show_graph(ont_net, "stage-2-ontology.html")')
        if index == 16:
            # The original initialized this only inside the range loop.
            source = source.replace("    return [list(r) for r in unique_relations]",
                                    "    unique_relations = set(tuple(r) for r in relations)\n"
                                    "    return [list(r) for r in sorted(\n"
                                    "        unique_relations, key=lambda triple: tuple(item.iri for item in triple)\n"
                                    "    )]")
        if index in (32, 33, 34):
            graph_expression, filename = source.strip().rsplit('.show("', 1)
            filename = filename.removesuffix('")')
            source = f'show_graph({graph_expression}, "{filename}")\n'
        if index == 38:
            source = source.replace('net.show("bn_network.html")',
                                    'show_graph(net, "bayesian-network.html")')
        if index == 42:
            for name in ("bn_compounds", "bn_proteins", "bn_genes", "bn_diseases"):
                source = source.replace(f"{name} = list(set({name}))",
                                        f"{name} = sorted(set({name}), key=lambda entity: entity.iri)")
        if index == 60:
            source = clean('''
                def getCompoundInfo(*compound_indices):
                    for rank, compound_index in enumerate(compound_indices, start=1):
                        compound = bn_compounds[int(compound_index)]
                        print(f"Rank {rank}: {compound.name}")
                        print(compound.WIKIPEDIA)
                        print(compound.NPASS)
                        getEffect(compound.has_effect)
                        print()
            ''')
        if index in (61, 68, 75, 82, 89):
            source = "getCompoundInfo(*counts.index[:3])\n"
        if "trace = mc.sample(" in source:
            source = "# Expensive original sampling request: one million draws per chain.\n" + source
    return source


def ontology_load() -> str:
    return clean('''
        if not OWL_PATH.is_file():
            raise FileNotFoundError(
                f"Ontology not found at {OWL_PATH}. Run Stage 1 with the original TSV tables first."
            )
        world = World()
        onto = world.get_ontology(OWL_PATH.as_uri()).load()
    ''')


def merge(notebooks: dict[str, dict], hashes: dict[str, str]) -> dict:
    cells = [cell("markdown", INTRO, "intro"), cell("markdown", SETUP_NOTE, "setup-note")]
    config = cell("code", CONFIG, "config")
    config["metadata"]["provenance"] = {
        "kind": "editorial-configuration",
        "derived_from": [
            {"source": "assessment-1", "original_cell_index": 1, "source_notebook_sha256": hashes["assessment-1"]},
            {"source": "assessment-2", "original_cell_index": 1, "source_notebook_sha256": hashes["assessment-2"]},
        ],
    }
    cells.append(config)
    omitted = {"assessment-1": {0, 1, 95}, "assessment-2": {1, 21, 91}}
    replacements = {"assessment-1": A1_MARKDOWN, "assessment-2": A2_MARKDOWN}
    for assessment in ("assessment-1", "assessment-2"):
        for index, original in enumerate(notebooks[assessment]["cells"]):
            if index in omitted[assessment]:
                continue
            revised = copy.deepcopy(original)
            old_source = "".join(original.get("source", []))
            if original["cell_type"] == "markdown":
                if index not in replacements[assessment]:
                    raise ValueError(f"Unreviewed markdown cell: {assessment} / {index}")
                new_source = clean(replacements[assessment][index])
            else:
                new_source = transform_code(assessment, index, old_source)
            revised["source"] = new_source.splitlines(keepends=True)
            revised["id"] = hashlib.sha256(f"{assessment}:{index}".encode()).hexdigest()[:12]
            revised["metadata"]["provenance"] = {
                "source": assessment,
                "original_cell_index": index,
                "source_notebook_sha256": hashes[assessment],
                "source_edited": new_source != old_source,
            }
            if original["cell_type"] == "code":
                revised["metadata"]["historical_outputs"] = {
                    "retained_from_original": True,
                    "regenerated_after_editorial_changes": False,
                    "original_execution_count": original.get("execution_count"),
                }
            cells.append(revised)
    cells.append(cell("markdown", REFLECTIONS, "reflections"))
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.12", "file_extension": ".py", "mimetype": "text/x-python", "pygments_lexer": "ipython3", "nbconvert_exporter": "python"},
            "study": {
                "author": "Ibrahim Ineizeh",
                "historical_analysis_year": 2025,
                "editorial_packaging_year": 2026,
                "historical_output_notice": "Stored outputs are copied from original notebooks and have not been regenerated after editorial and portability changes.",
                "original_sources": [{"source": key, "sha256": hashes[key]} for key in hashes],
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def verify(notebook: dict, notebooks: dict[str, dict]) -> None:
    import nbformat

    nbformat.validate(nbformat.from_dict(notebook))
    code_count = 0
    retained_output_count = 0
    for position, entry in enumerate(notebook["cells"]):
        if entry["cell_type"] != "code":
            continue
        code_count += 1
        source = "".join(entry["source"])
        ast.parse(source, filename=f"merged-cell-{position}", mode="exec")
        compile(source, f"merged-cell-{position}", "exec")
        provenance = entry["metadata"].get("provenance", {})
        if provenance.get("source"):
            original = notebooks[provenance["source"]]["cells"][provenance["original_cell_index"]]
            if entry.get("outputs", []) != original.get("outputs", []):
                raise ValueError(f"Historical outputs changed in cell {position}")
            retained_output_count += len(entry.get("outputs", []))
    print(f"Validated {len(notebook['cells'])} cells; compiled {code_count} code cells; retained {retained_output_count} original output records.")


def find_source(source_root: Path, identifier: str, override: Path | None) -> Path:
    if override is not None:
        return override
    candidates = sorted((source_root / SOURCE_DIRS[identifier]).glob("*code.ipynb"))
    if len(candidates) != 1:
        raise FileNotFoundError(
            f"Expected one historical notebook for {identifier}. "
            "Provide --source-root or the corresponding --assessment-one/--assessment-two path. "
            "The prebuilt public notebook does not require these private sources."
        )
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=PACKAGE_ROOT.parent)
    parser.add_argument("--assessment-one", type=Path)
    parser.add_argument("--assessment-two", type=Path)
    parser.add_argument("--output", type=Path, default=PACKAGE_ROOT / "notebooks" / "oregano-study.ipynb")
    args = parser.parse_args()
    paths = {
        "assessment-1": find_source(args.source_root, "assessment-1", args.assessment_one),
        "assessment-2": find_source(args.source_root, "assessment-2", args.assessment_two),
    }
    blobs = {key: value.read_bytes() for key, value in paths.items()}
    notebooks = {key: json.loads(value) for key, value in blobs.items()}
    hashes = {key: hashlib.sha256(value).hexdigest() for key, value in blobs.items()}
    notebook = merge(notebooks, hashes)
    verify(notebook, notebooks)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

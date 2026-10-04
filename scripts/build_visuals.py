#!/usr/bin/env python3
"""Rebuild publication figures and offline graph views from committed exports.

Usage: python scripts/build_visuals.py
Requires matplotlib (and its numpy dependency). No original notebooks, ontology,
remote services, or posterior traces are required. This does not rerun inference.
"""
from __future__ import annotations

import csv
import html
import json
import os
from pathlib import Path
import textwrap

os.environ.setdefault("MPLCONFIGDIR", "/tmp/oregano-public-matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import FuncFormatter, LogLocator

ROOT = Path(__file__).resolve().parents[1]
RESULTS, FIGURES, VIEWS = ROOT / "results", ROOT / "figures", ROOT / "visualizations"
NAVY, TEAL, PALE, GREY = "#153247", "#207c80", "#edf5f5", "#586b77"
LIGHT, WHITE = "#d5e2e7", "#ffffff"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 15,
    "axes.labelsize": 10, "text.color": NAVY, "axes.labelcolor": GREY,
    "xtick.color": GREY, "ytick.color": NAVY, "axes.edgecolor": LIGHT,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": WHITE, "axes.facecolor": WHITE,
    "svg.fonttype": "none", "savefig.facecolor": WHITE,
})


def rows(name):
    with (RESULTS / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig, name):
    FIGURES.mkdir(exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(FIGURES / f"{name}.{ext}", dpi=190, bbox_inches="tight", pad_inches=0.2,
                    metadata={"Creator": "OREGANO research portfolio"})
    plt.close(fig)


def frame(title, subtitle, figsize):
    fig = plt.figure(figsize=figsize)
    fig.text(0.045, 0.965, title, fontsize=20, fontweight="bold", va="top")
    fig.text(0.045, 0.922, subtitle, fontsize=10.5, color=GREY, va="top")
    return fig


def foot(fig, text):
    fig.text(0.045, 0.022, text, color=GREY, fontsize=8.5, va="bottom")


def box(ax, x, y, width, height, text, *, fill=PALE, edge=LIGHT, size=10, bold=False):
    ax.add_patch(FancyBboxPatch((x-width/2, y-height/2), width, height,
                 boxstyle="round,pad=0.01,rounding_size=0.012", linewidth=1,
                 facecolor=fill, edgecolor=edge))
    ax.text(x, y, text, ha="center", va="center", fontsize=size,
            fontweight="bold" if bold else "normal", linespacing=1.45)


def arrow(ax, start, end, text="", *, color=TEAL, text_y=None, style="-"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                 lw=1.7, color=color, linestyle=style, connectionstyle="arc3,rad=0"))
    if text:
        x=(start[0]+end[0])/2
        y=(start[1]+end[1])/2 + 0.035 if text_y is None else text_y
        ax.text(x, y, text, fontsize=8.3, ha="center", va="bottom", color=GREY)


def workflow():
    data = rows("workflow.csv")
    fig = frame("The research process", "Two assessments, one progression from graph construction to exploratory inference.", (13.4, 7.7))
    ax=fig.add_axes((0.04,0.09,0.92,0.76));ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    xs=[0.16,0.50,0.84];ys=[0.73,0.27]
    for i,r in enumerate(data):
        x,y=xs[i%3],ys[i//3]
        box(ax,x,y,.28,.31,"",fill=PALE if i<3 else "#f3f6f8")
        ax.text(x-.115,y+.112,f"0{r['step']}  ·  {r['phase'].upper()}",color=TEAL,fontsize=9,fontweight="bold")
        ax.text(x,y+.045,r["title"],ha="center",fontsize=12,fontweight="bold")
        ax.text(x,y-.05,r["detail"],ha="center",va="center",color=GREY,fontsize=9.2,linespacing=1.65)
        if i%3<2:arrow(ax,(x+.155,y),(xs[i%3+1]-.155,y))
    # Numbering keeps the transition between the two rows unambiguous.
    ax.text(.5,.50,"BUILD AND EXPLORE  →  TRACE, MODEL, AND REVIEW",ha="center",color=TEAL,fontsize=9,fontweight="bold")
    foot(fig,"Source: saved Assessment 1 and Assessment 2 cells; individual step provenance is recorded in results/workflow.csv.")
    save(fig,"workflow")


def graph_composition():
    ent=sorted(rows("entity_counts.csv"),key=lambda r:int(r["count"]),reverse=True)
    rel=sorted(rows("relation_counts.csv"),key=lambda r:int(r["count"]),reverse=True)
    summary=f"{sum(int(r['count']) for r in ent):,} entity instances  ·  {sum(int(r['count']) for r in rel):,} retained object assertions  ·  {len(ent)} entity types  ·  {len(rel)} relation types"
    fig=frame("The constructed knowledge graph", summary, (14.5,9.3))
    left=fig.add_axes((.145,.17,.295,.66));right=fig.add_axes((.69,.17,.245,.66))
    for ax,data,key,title in [(left,ent,"entity","Entity composition"),(right,rel,"relation","Relation assertions")]:
        values=[int(r["count"]) for r in data]
        labels=[r[key].replace("_"," ").title() if key=="entity" else r[key] for r in data]
        ax.barh(range(len(data)),values,color=TEAL if key=="entity" else NAVY,height=.64)
        ax.set_yticks(range(len(data)),labels);ax.invert_yaxis();ax.set_xscale("log")
        ax.set_xlim(50 if key=="entity" else 100, max(values)*3.7)
        ax.set_xlabel("Count (logarithmic scale)",labelpad=12)
        ax.set_title(title,loc="left",fontweight="bold",pad=18)
        ax.grid(axis="x",which="major",color=LIGHT,linewidth=.7);ax.set_axisbelow(True)
        ax.xaxis.set_major_locator(LogLocator(base=10,numticks=5))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f"{x:,.0f}"))
        ax.tick_params(axis="y",length=0,labelsize=9.5,pad=8)
        for i,v in enumerate(values):ax.text(v*1.12,i,f"{v:,}",va="center",fontsize=8.8)
        ax.spines["left"].set_visible(False)
    foot(fig,"Source: Assessment 1 saved cells 33 (entities) and 28 (relations). Totals sum the recorded counts; has_code is excluded.")
    save(fig,"graph_composition")


def candidate_paths():
    data=rows("candidate_paths.csv")
    fig=frame("Three paths with matching indication codes", "Recorded compound → protein → gene → disease paths; each disease UMLS code matches the compound indication code.",(14.2,9.0))
    ax=fig.add_axes((.035,.105,.93,.75));ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    xs=[.11,.37,.63,.89];width=.18
    for i,r in enumerate(data):
        y=.82-i*.30
        disease=textwrap.fill(r["disease_label"],24)
        labels=[f"{r['compound_label']}\n{r['compound_id']}",f"Protein\n{r['protein_id']}",f"Gene\n{r['gene_id']}",f"{disease}\n{r['disease_id']}"]
        for j,label in enumerate(labels):box(ax,xs[j],y,width,.15,label,fill=PALE if j in [0,3] else "#f3f6f8",size=9.2,bold=j==0)
        for j,name in enumerate(["has_target","gene_product_of","causes_condition"]):
            arrow(ax,(xs[j]+width/2+.014,y),(xs[j+1]-width/2-.014,y),name,text_y=y+.089)
        ax.text(.89,y-.115,f"UMLS = SIDER: {r['disease_umls']}",ha="center",fontsize=9,color=TEAL,fontweight="bold")
        ax.text(.11,y-.115,"Recorded indication association",ha="center",fontsize=8.3,color=GREY)
        if i<2:ax.plot([.015,.985],[y-.18,y-.18],color=LIGHT,lw=.8)
    foot(fig,"Source: Assessment 2 saved cell 30; path edges cross-checked against saved graph assets. These are recorded indication associations, without independent clinical validation.")
    save(fig,"candidate_paths")


def trioxide_paths():
    data=rows("trioxide_candidate_paths.csv")
    fig=frame("Additional arsenic trioxide candidate paths", "Three further disease connections retained from the original analysis; identifiers are shown without unverified disease labels.",(13.7,7.3))
    ax=fig.add_axes((.04,.16,.92,.66));ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    xs=[.12,.385,.64,.90];width=.18
    box(ax,xs[0],.50,width,.19,f"{data[0]['compound_label']}\n{data[0]['compound_id']}",bold=True,size=10)
    groups=list(dict.fromkeys((r['protein_id'],r['gene_id']) for r in data))
    for (protein,gene),y in zip(groups,[.69,.21]):
        box(ax,xs[1],y,width,.14,f"Protein\n{protein}",size=10)
        box(ax,xs[2],y,width,.14,f"Gene\n{gene}",size=10)
    for r,y in zip(data,[.86,.53,.21]):box(ax,xs[3],y,width,.13,r['disease_id'],size=10)
    for y in [.69,.21]:
        arrow(ax,(xs[0]+.10,.50),(xs[1]-.10,y))
        arrow(ax,(xs[1]+.105,y),(xs[2]-.105,y),"gene_product_of",text_y=y+.09)
    ax.text(.22,.70,"has_target",fontsize=8.6,color=GREY,rotation=21)
    ax.text(.22,.30,"has_target",fontsize=8.6,color=GREY,rotation=-24)
    for y,z in [(.69,.86),(.69,.53),(.21,.21)]:arrow(ax,(xs[2]+.105,y),(xs[3]-.105,z))
    ax.text(.78,.72,"causes_condition",fontsize=8.2,color=GREY,ha="center")
    ax.text(.78,.31,"causes_condition",fontsize=8.2,color=GREY,ha="center")
    foot(fig,"Source: Assessment 2 cell 35 and read-only edge checks in its saved OWL. Graph connectivity alone does not validate a treatment.")
    save(fig,"trioxide_paths")


def bayesian_network():
    graph=json.loads((VIEWS/"data/bayesian_network.json").read_text())
    fig=frame("The exploratory Bayesian network", "A categorical model built from graph structure and heuristic conditional probability tables.",(11.8,7.4))
    ax=fig.add_axes((.09,.22,.82,.57));ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    coords={"Compound":(.12,.51),"Gene":(.44,.80),"Protein":(.60,.25),"Disease":(.88,.25)}
    for node in graph["nodes"]:
        x,y=coords[node["id"]];box(ax,x,y,.17,.17,node["id"],fill=PALE,bold=True,size=12)
    for edge in graph["edges"]:
        a,b=coords[edge["from"]],coords[edge["to"]]
        dx,dy=b[0]-a[0],b[1]-a[1];norm=(dx*dx+dy*dy)**.5
        arrow(ax,(a[0]+dx/norm*.11,a[1]+dy/norm*.11),(b[0]-dx/norm*.11,b[1]-dy/norm*.11))
    fig.text(.5,.155,r"$P(C,G,P,D)=P(C)\,P(G\mid C)\,P(P\mid G,C)\,P(D\mid P)$",ha="center",fontsize=17)
    foot(fig,"Source: Assessment 2 cells 38–39. Arrows describe the implemented model; they do not establish biological causation or treatment efficacy.")
    save(fig,"bayesian_network")


def posterior_rankings():
    data=rows("bayesian_rankings.csv")
    ids=list(dict.fromkeys(r["disease_id"] for r in data))
    fig=frame("Saved Bayesian rankings", "Top three recorded compound counts for each observed disease ID. Labels follow the saved UMLS identifiers.",(14.1,11.0))
    grids=fig.add_gridspec(3,2,left=.19,right=.96,bottom=.105,top=.84,hspace=1.0,wspace=.83)
    for i,did in enumerate(ids):
        ax=fig.add_subplot(grids[i//2,i%2])
        group=sorted([r for r in data if r["disease_id"]==did],key=lambda r:int(r["rank"]))
        vals=[int(r["posterior_sample_count"]) for r in group]
        labels=[(r["compound_label"] or r["compound_npass"])+"\n"+r["compound_id"] for r in group]
        ax.barh(range(3),vals,color=[TEAL,NAVY,"#658999"],height=.64)
        ax.set_yticks(range(3),labels);ax.invert_yaxis();ax.set_xlim(0,140000)
        ax.set_title(f"{group[0]['disease_label']}\n{did}",loc="left",fontsize=11.4,fontweight="bold",pad=14)
        ax.tick_params(axis="y",length=0,labelsize=9,pad=7)
        ax.set_xlabel("Posterior sample count",fontsize=9,labelpad=7)
        ax.set_xticks([0,50000,100000]);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f"{x:,.0f}"))
        ax.tick_params(axis="x",labelsize=8.5)
        ax.grid(axis="x",color=LIGHT,lw=.6);ax.set_axisbelow(True);ax.spines["left"].set_visible(False)
        for j,v in enumerate(vals):ax.text(v+2600,j,f"{v:,}",va="center",fontsize=8.8)
    note=fig.add_subplot(grids[2,1]);note.axis("off")
    note.text(0,1,"Interpretation",fontsize=12,fontweight="bold",va="top")
    note.text(0,.78,"Counts are raw saved output.\nNo verified full denominator is available.\n\nRanks depend on the chosen graph subset\nand heuristic probability tables.\nThey are not clinical treatment probabilities.",va="top",fontsize=10,color=GREY,linespacing=1.7)
    foot(fig,"Source: Assessment 2 cells 58, 67, 74, 81, 88; compound metadata from cells 61, 68, 75, 82, 89 and saved OWL. Original prose labels remain in the CSV.")
    save(fig,"posterior_rankings")


CSS = """*{box-sizing:border-box}body{margin:0;background:#f5f8fa;color:#153247;font:15px/1.55 system-ui,-apple-system,sans-serif}header{padding:22px 32px 16px;background:white;border-bottom:1px solid #d5e2e7}header a{color:#207c80;text-decoration:none;font-size:13px}h1{font-size:25px;letter-spacing:-.5px;margin:6px 0}p{margin:5px 0;color:#586b77}.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:13px 32px;background:#edf5f5;border-bottom:1px solid #d5e2e7}input,select,button{font:inherit;border:1px solid #c5d6dc;border-radius:5px;background:white;padding:7px 12px;color:#153247}button{cursor:pointer}button:hover{border-color:#207c80}input{min-width:240px}.toolbar label{font-size:13px;color:#586b77}#network{height:calc(100vh - 235px);min-height:440px;background:white}footer{padding:12px 32px;font-size:12px;color:#586b77;border-top:1px solid #d5e2e7}.legend{display:flex;gap:14px;flex-wrap:wrap;padding:10px 32px;background:white;font-size:12px}.legend span:before{content:'';display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--c);margin-right:5px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin:25px 32px}.card{display:block;padding:20px;background:white;border:1px solid #d5e2e7;border-radius:7px;text-decoration:none;color:#153247}.card:hover{border-color:#207c80}.card strong{font-size:17px}.card small{display:block;margin-top:8px;color:#586b77}#status{margin-left:auto;font-size:12px;color:#586b77}@media(max-width:650px){header,.toolbar,footer,.legend{padding-left:16px;padding-right:16px}#network{height:65vh}.toolbar input{min-width:160px}}
"""

JS = """'use strict';
const data=window.GRAPH_DATA;
const palette={COMPOUND:'#207c80',PROTEIN:'#315a76',GENE:'#788d99',GENES:'#788d99',DISEASE:'#8e6a74',DISEASES:'#8e6a74',PHENOTYPE:'#a5b5bd',PHENOTYPES:'#a5b5bd',MOLECULE:'#57a3a5',ACTIVITY:'#8c899c',EFFECT:'#b39e72',INDICATION:'#658b88',SIDE_EFFECT:'#a98a75',PATHWAY:'#7a9eae',PATHWAYS:'#7a9eae'};
const escape=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
function entity(n){const text=String(n.title||n.label||n.id).toUpperCase();if(data.slug==='bayesian_network')return String(n.id).toUpperCase();for(const kind of Object.keys(palette).sort((a,b)=>b.length-a.length)){if(text===kind||text.startsWith(kind+'_')||text.startsWith(kind+'\\n')||text.startsWith(kind+'/'))return kind;}return text.split(/[ _/\\n]/)[0];}
const allNodes=data.nodes.map(n=>{const kind=entity(n),focus=n.shape==='diamond';let label=String(n.label||n.id);if(data.slug!=='ontology'&&data.slug!=='bayesian_network')label=String(n.title||n.id).split('/')[0];return {...n,label,title:escape(n.title||label),kind,shape:focus?'diamond':'dot',size:focus?24:(data.nodes.length>1000?5:10),borderWidth:focus?3:1,color:{background:palette[kind]||'#658999',border:focus?'#153247':'#ffffff'},font:{size:data.nodes.length>1000?0:11,color:'#153247'},hidden:false};});
const allEdges=data.edges.map((e,i)=>({...e,id:i,title:escape(e.title||e.label||''),color:e.title==='increase_efficacy'?'#207c80':e.title==='decrease_efficacy'?'#6a7892':'#a9bdc7',width:1,arrows:'to',smooth:{enabled:true,type:'continuous',roundness:.18}}));
const nodes=new vis.DataSet(allNodes),edges=new vis.DataSet(allEdges);
const small=data.nodes.length<20;
const options={nodes:{chosen:true},edges:{arrowStrikethrough:false},interaction:{hover:true,navigationButtons:true,keyboard:true,hideEdgesOnDrag:data.nodes.length>1000},physics:{enabled:!small,solver:'barnesHut',barnesHut:{gravitationalConstant:-3500,centralGravity:.2,springLength:110,springConstant:.03,avoidOverlap:.3},stabilization:{enabled:true,iterations:data.nodes.length>1000?120:240,updateInterval:30}},layout:{randomSeed:23},configure:false};
if(data.slug==='bayesian_network'){const pos={Compound:{x:0,y:20},Gene:{x:190,y:-120},Protein:{x:300,y:160},Disease:{x:540,y:160}};nodes.update(allNodes.map(n=>({...n,...pos[n.id],fixed:true,size:27,font:{size:16,color:'#153247'}})));}
if(data.slug==='ontology'){options.physics.enabled=true;options.physics.stabilization.iterations=500;options.physics.barnesHut.springLength=240;nodes.update(allNodes.map(n=>({...n,size:20,font:{size:14,color:'#153247'}})));edges.update(allEdges.map(e=>({...e,font:{size:9,color:'#586b77',strokeWidth:3,strokeColor:'#ffffff'},smooth:{enabled:true,type:'curvedCW',roundness:.2}})));}
const network=new vis.Network(document.getElementById('network'),{nodes,edges},options);
const kinds=[...new Set(allNodes.map(n=>n.kind))].sort();
const select=document.getElementById('type');for(const kind of kinds){const o=document.createElement('option');o.value=kind;o.textContent=kind.toLowerCase().replace('_',' ');select.appendChild(o);const item=document.createElement('span');item.textContent=o.textContent;item.style.setProperty('--c',palette[kind]||'#658999');document.getElementById('legend').appendChild(item);}
const status=document.getElementById('status');status.textContent=`${allNodes.length.toLocaleString()} nodes · ${allEdges.length.toLocaleString()} edges`;
let moving=options.physics.enabled;
network.once('stabilizationIterationsDone',()=>{moving=false;network.setOptions({physics:{enabled:false}});document.getElementById('physics').textContent='Enable movement';network.fit({animation:false});});
document.getElementById('fit').onclick=()=>network.fit({animation:true});
document.getElementById('physics').textContent=moving?'Pause movement':'Enable movement';document.getElementById('physics').onclick=()=>{moving=!moving;network.setOptions({physics:{enabled:moving}});document.getElementById('physics').textContent=moving?'Pause movement':'Enable movement';};
select.onchange=()=>{const kind=select.value;const visible=new Set(allNodes.filter(n=>!kind||n.kind===kind).map(n=>n.id));nodes.update(allNodes.map(n=>({id:n.id,hidden:!visible.has(n.id)})));const es=allEdges.map(e=>({id:e.id,hidden:!visible.has(e.from)||!visible.has(e.to)}));edges.update(es);status.textContent=`${visible.size.toLocaleString()} nodes · ${es.filter(e=>!e.hidden).length.toLocaleString()} edges`;network.fit({animation:true});};
function search(){const term=document.getElementById('search').value.trim().toLowerCase();if(!term)return;const matches=allNodes.filter(n=>String(n.id).toLowerCase().includes(term)||String(n.title).toLowerCase().includes(term)||String(n.label).toLowerCase().includes(term));if(!matches.length){status.textContent='No matching node';return;}select.value='';select.onchange();network.selectNodes(matches.map(n=>n.id));if(matches.length===1)network.focus(matches[0].id,{scale:1.5,animation:true});else network.fit({nodes:matches.map(n=>n.id),animation:true});status.textContent=`${matches.length} matching node${matches.length===1?'':'s'}`;}
document.getElementById('find').onclick=search;document.getElementById('search').onkeydown=e=>{if(e.key==='Enter')search();};
document.getElementById('reset').onclick=()=>{document.getElementById('search').value='';select.value='';select.onchange();network.unselectAll();};
"""


def interactive_views():
    VIEWS.mkdir(exist_ok=True)
    (VIEWS/"style.css").write_text(CSS)
    (VIEWS/"graph.js").write_text(JS)
    assets=[]
    for path in sorted((VIEWS/"data").glob("*.json")):
        graph=json.loads(path.read_text());slug=graph["slug"]
        embedded=json.dumps(graph,ensure_ascii=False).replace("</","<\\/")
        title,sub=html.escape(graph["title"]),html.escape(graph["subtitle"])
        page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} — OREGANO</title><link rel="stylesheet" href="vendor/vis-network.css"><link rel="stylesheet" href="style.css"><script src="vendor/vis-network.min.js"></script></head>
<body><header><a href="index.html">← All visualizations</a><h1>{title}</h1><p>{sub}</p></header>
<div class="toolbar"><input id="search" aria-label="Find a node" placeholder="Find an ID or compound name"><button id="find">Find</button><label>Entity <select id="type"><option value="">All types</option></select></label><button id="fit">Fit graph</button><button id="physics">Enable movement</button><button id="reset">Reset</button><span id="status"></span></div>
<div id="legend" class="legend"></div><div id="network" role="img" aria-label="Interactive directed knowledge graph"></div>
<footer>Drag to pan, scroll to zoom, and hover for identifiers or relation names. Source: {graph['source_notebook'].replace('_',' ').title()}, original cell {graph['source_cell']} (zero-based). Graph connectivity is exploratory evidence. All runtime assets are bundled locally.</footer>
<script>window.GRAPH_DATA={embedded};</script><script src="graph.js"></script></body></html>'''
        (VIEWS/f"{slug}.html").write_text(page)
        assets.append(graph)
    cards=''.join(f'<a class="card" href="{a["slug"]}.html"><strong>{html.escape(a["title"])}</strong><small>{len(a["nodes"]):,} nodes · {len(a["edges"]):,} edges</small><p>{html.escape(a["subtitle"])}</p></a>' for a in assets)
    (VIEWS/"index.html").write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Interactive visualizations — OREGANO</title><link rel="stylesheet" href="style.css"></head><body><header><a href="../README.md">← Project overview</a><h1>Interactive visualizations</h1><p>Saved research graph views, repackaged with local assets. Samples retain their original nodes and edges.</p></header><main class="grid">{cards}</main><footer>Views open locally without a server or network connection. Static publication figures are available in the figures folder.</footer></body></html>''')


def main():
    for build in (workflow,graph_composition,candidate_paths,trioxide_paths,bayesian_network,posterior_rankings,interactive_views):
        build()
        print(f"Built {build.__name__}")


if __name__ == "__main__":
    main()

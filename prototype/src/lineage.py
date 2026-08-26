"""
lineage.py
----------
Generate simple data lineage artifacts from analysis output.

Produces:
 - lineage.json: adjacency list of nodes/edges
 - lineage.dot: Graphviz DOT file (can be rendered by local graphviz)
 - lineage_mermaid.md: Merlin/mermaid flowchart snippet (also embedded in report)

This is intentionally lightweight (no extra runtime deps). For interactive
visualization, import lineage.json into an external graph tool or render
lineage.dot with Graphviz.
"""
from typing import Dict, List
import json
import os


def _normalize_name(n: str) -> str:
    return n.strip().replace(" ", "_")


def generate_lineage_graph(analysis: Dict, output_dir: str, metadata_findings: Dict = None) -> Dict:
    """Generate lineage artifacts from analysis, optionally enriched with column-level usage.

    If metadata_findings contains 'used_columns_by_table', produce column-level
    nodes and edges where possible. Falls back to table-level lineage otherwise.

    Returns a dict with paths to written files and a simple nodes/edges dict.
    """
    nodes = set()
    edges = []

    deps = analysis.get("dependencies", []) or []

    used_cols = {}
    if metadata_findings:
        used_cols = metadata_findings.get("used_columns_by_table", {}) or {}

    # Helper to create fully-qualified node names
    def col_node(table: str, col: str) -> str:
        return _normalize_name(f"{table}.{col}")

    # First pass: add table-level nodes
    for tbl in analysis.get("tables", []):
        nodes.add(_normalize_name(tbl))

    # If we have column usage information, add column nodes
    if used_cols:
        for t, cols in used_cols.items():
            for c in cols:
                nodes.add(col_node(t, c))
                # optionally also keep table node (already added)

    # Build edges from dependencies; prefer column-level edges when both sides have columns
    for dep in deps:
        if " depends on " in dep:
            child, parents = dep.split(" depends on ")
            child = child.strip()
            child_n = _normalize_name(child)
            nodes.add(child_n)
            parent_list = [p.strip() for p in parents.split(",")]
            for p in parent_list:
                parent_n = _normalize_name(p)
                nodes.add(parent_n)
                # If both parent and child have column usage info, link matching columns
                parent_cols = set([str(x) for x in used_cols.get(p, [])])
                child_cols = set([str(x) for x in used_cols.get(child, [])])
                if parent_cols and child_cols:
                    # link intersection columns
                    intersect = parent_cols.intersection(child_cols)
                    if intersect:
                        for col in sorted(intersect):
                            edges.append({"from": col_node(p, col), "to": col_node(child, col)})
                    else:
                        # no direct column name matches; create edges from each parent col -> child table
                        for col in sorted(parent_cols):
                            edges.append({"from": col_node(p, col), "to": child_n})
                        for col in sorted(child_cols):
                            edges.append({"from": parent_n, "to": col_node(child, col)})
                else:
                    # fallback to table-level edge
                    edges.append({"from": parent_n, "to": child_n})
        else:
            n = _normalize_name(dep)
            nodes.add(n)

    # Build adjacency map including columns
    nodes = sorted(list(nodes))
    adjacency = {n: [] for n in nodes}
    for e in edges:
        adjacency.setdefault(e["from"], []).append(e["to"])

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "lineage.json")
    dot_path = os.path.join(output_dir, "lineage.dot")
    mermaid_path = os.path.join(output_dir, "lineage_mermaid.md")

    with open(json_path, "w") as jf:
        json.dump({"nodes": nodes, "edges": edges, "adjacency": adjacency}, jf, indent=2)

    # Write DOT
    with open(dot_path, "w") as df:
        df.write("digraph lineage {\n")
        df.write("  rankdir=LR;\n")
        for n in nodes:
            df.write(f'  "{n}";\n')
        for e in edges:
            df.write(f'  "{e["from"]}" -> "{e["to"]}";\n')
        df.write("}\n")

    # Write mermaid flowchart (best-effort: only include table-level edges)
    with open(mermaid_path, "w") as mf:
        mf.write("```mermaid\nflowchart LR\n")
        for e in edges:
            # if either side contains a '.', skip for readability in mermaid
            if "." in e["from"] or "." in e["to"]:
                continue
            mf.write(f'    {e["from"].replace("-","_")} --> {e["to"].replace("-","_")}\n')
        mf.write("```\n")

    return {"json": json_path, "dot": dot_path, "mermaid": mermaid_path, "nodes": nodes, "edges": edges}

"""
migration_planner.py
--------------------
Deterministic migration planner that sequences migration steps based on
analysis dependencies and validation results. Rule-based, no LLM calls.

Produces a plan dict suitable for writing to JSON and inclusion in the
migration report. See docs/architecture.md (Migration Planning stage).
"""

from typing import Dict, List, Set


def _parse_dependencies(dep_strings: List[str]) -> Dict[str, Set[str]]:
    """Parse dependency statements of the form "child depends on parent1, parent2".
    Returns graph as adjacency list: parent -> set(children)
    """
    graph = {}
    for d in dep_strings:
        if " depends on " in d:
            parts = d.split(" depends on ")
            child = parts[0].strip()
            parents = [p.strip() for p in parts[1].split(",") if p.strip()]
            for p in parents:
                graph.setdefault(p, set()).add(child)
            # ensure child node exists
            graph.setdefault(child, set())
    return graph


def _topological_sort(nodes: Set[str], graph: Dict[str, Set[str]]) -> List[str]:
    """Perform Kahn's algorithm. Graph is parent->children. Returns ordered list.
    Any nodes not in graph are appended at the end in sorted order for
    determinism.
    """
    # build incoming edge count
    incoming = {n: 0 for n in nodes}
    for parent, children in graph.items():
        for c in children:
            if c in incoming:
                incoming[c] += 1
            else:
                incoming[c] = 1
        if parent not in incoming:
            incoming[parent] = incoming.get(parent, 0)

    # start with nodes that have 0 incoming
    zero = sorted([n for n, c in incoming.items() if c == 0])
    order = []
    g = {k: set(v) for k, v in graph.items()}

    while zero:
        n = zero.pop(0)
        order.append(n)
        for child in sorted(g.get(n, [])):
            incoming[child] -= 1
            if incoming[child] == 0:
                zero.append(child)
        g.pop(n, None)
        zero = sorted(zero)

    # append any remaining nodes not processed
    remaining = [n for n in nodes if n not in order]
    order.extend(sorted(remaining))
    return order


def generate_migration_plan(analysis: Dict, validation: Dict) -> Dict:
    """Generate a simple deterministic migration plan.

    Plan keys:
      - steps: ordered list of {order, table, effort, rules_touching, blocking}
      - blocking_items: list of strings describing blocking validation failures
    """
    tables = analysis.get("tables", [])
    deps = analysis.get("dependencies", [])
    rules = analysis.get("business_rules", [])

    nodes = set(tables)
    graph = _parse_dependencies(deps)

    order = _topological_sort(nodes, graph)

    # Map rules touching tables by simple keyword presence
    rules_by_table = {t: [] for t in tables}
    for r in rules:
        text = (r.get("name", "") + " " + r.get("description", "")).lower()
        for t in tables:
            if t.lower() in text:
                rules_by_table.setdefault(t, []).append(r)

    # Determine blocking items from validation
    blocking_items = []
    for chk in validation.get("checks_failed", []):
        blocking_items.append(f"Validation failed: {chk}")

    # Also block on ambiguous rules
    ambiguous_rules = [r for r in rules if r.get("ambiguity_flag")]
    for ar in ambiguous_rules:
        blocking_items.append(f"Ambiguous rule: {ar.get('id')} - {ar.get('name')}")

    steps = []
    for idx, t in enumerate(order, start=1):
        touching = rules_by_table.get(t, [])
        num_rules = len(touching)
        has_amb = any(r.get("ambiguity_flag") for r in touching)
        # effort heuristic
        if has_amb or num_rules >= 3:
            effort = "High"
        elif num_rules == 0:
            effort = "Low"
        else:
            effort = "Medium"
        blocking = False
        notes = []
        # if any blocking items mention this table or any of its rules, mark blocking
        for bi in blocking_items:
            if t.lower() in bi.lower():
                blocking = True
                notes.append(bi)
        steps.append({
            "order": idx,
            "table": t,
            "effort": effort,
            "rules_touching": [r.get("id") for r in touching],
            "blocking": blocking,
            "notes": notes,
        })

    return {"steps": steps, "blocking_items": blocking_items, "ordered_tables": order}

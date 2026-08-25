"""
metadata_interpreter.py
-----------------------
Interpret and cross-reference declared metadata (prototype/sample_legacy/legacy_metadata.json)
against actual SQL usage found in legacy assets.

See docs/architecture.md (AI Analysis Layer: metadata interpretation).
"""

import json
import re
from typing import Dict, List, Set


def _find_aliases(sql_text: str) -> Dict[str, str]:
    """Find simple FROM/JOIN alias declarations like: FROM raw_orders o
    Returns mapping alias -> table_name
    """
    alias_map = {}
    # Match patterns like: FROM <table> <alias> or JOIN <table> <alias>
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_\.]+)\s+([a-zA-Z0-9_]+)", sql_text, re.IGNORECASE):
        table = m.group(1).strip()
        alias = m.group(2).strip()
        alias_map[alias] = table
    return alias_map


def _extract_select_columns(sql_text: str) -> List[Dict]:
    """Extract columns used in SELECT lists across the SQL text.
    Returns list of dicts: {"columns": [list of column tokens], "from_tables": [tables in FROM/JOIN for that select]}
    This is heuristic and designed for the PoC's sample SQL style.
    """
    selects = []
    # Find SELECT ... FROM blocks (non-greedy)
    for m in re.finditer(r"SELECT\s+(.*?)\s+FROM\s+([a-zA-Z0-9_\.,\s]+)", sql_text, re.IGNORECASE | re.DOTALL):
        select_list = m.group(1)
        from_clause = m.group(2)
        # split select_list by commas at top level
        parts = [p.strip() for p in re.split(r",\s*(?![^()]*\))", select_list) if p.strip()]
        cols = []
        for p in parts:
            # Try to find alias.column patterns or bare column names
            # Remove common expressions like UPPER(...), ROUND(...)
            token = p
            # remove function calls
            token = re.sub(r"[a-zA-Z_][a-zA-Z0-9_]*\s*\(|\)$", "", token)
            # find last word or alias.word
            m2 = re.search(r"([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)|([a-zA-Z0-9_]+)$", token)
            if m2:
                cols.append(m2.group(0))
        # find table names in from_clause (simple extraction of words separated by commas/joins)
        tables = [t.strip().split()[0] for t in re.split(r",|JOIN", from_clause) if t.strip()]
        selects.append({"columns": cols, "from_tables": tables})
    return selects


def _find_qualified_columns(sql_text: str) -> Set[str]:
    """Find occurrences of qualified columns like alias.col or table.col"""
    return set(re.findall(r"\b([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)\b", sql_text))


def _find_arithmetic_usage(sql_text: str) -> Set[str]:
    """Find columns that appear in arithmetic expressions (heuristic)."""
    cols = set()
    # look for patterns like col * col or col * number, col + col, etc.
    for m in re.finditer(r"\b([a-zA-Z0-9_]+)\b\s*\*|\*\s*\b([a-zA-Z0-9_]+)\b", sql_text):
        for g in m.groups():
            if g:
                cols.add(g)
    # also numeric operations with + - /
    for m in re.finditer(r"\b([a-zA-Z0-9_]+)\b\s*[\+\-\/]", sql_text):
        cols.add(m.group(1))
    for m in re.finditer(r"[\+\-\/]\s*\b([a-zA-Z0-9_]+)\b", sql_text):
        cols.add(m.group(1))
    return cols


def interpret_metadata(metadata_json: Dict, sql_text: str) -> Dict:
    """Cross-reference declared metadata against SQL usage.

    Returns a dict with keys:
      - undocumented_columns: list of {table, column}
      - unused_metadata_columns: list of {table, column}
      - inconsistent_comments: list of {table, column, comment, reason}

    This function uses heuristics suitable for the prototype sample and is
    not a full SQL parser. See docs/architecture.md (AI Analysis Layer).
    """
    # normalize table names to lower for matching
    metadata = {t.lower(): {c.lower(): v for c, v in data.get("columns", {}).items()} for t, data in metadata_json.items()}

    alias_map = _find_aliases(sql_text)
    qualified = _find_qualified_columns(sql_text)
    selects = _extract_select_columns(sql_text)
    arithmetic_cols = _find_arithmetic_usage(sql_text)

    used_cols_by_table = {}

    # Process qualified columns first (alias.col or table.col)
    for q in qualified:
        left, col = q.split(".")
        table = None
        if left in alias_map:
            table = alias_map[left]
        else:
            table = left
        # normalize
        table_l = table.lower()
        col_l = col.lower()
        used_cols_by_table.setdefault(table_l, set()).add(col_l)

    # Process select contexts: assign unqualified columns to from_tables if possible
    for s in selects:
        tables = [t.split()[0].lower() for t in s.get("from_tables", [])]
        cols = s.get("columns", [])
        for col_token in cols:
            if "." in col_token:
                continue
            col_l = col_token.lower()
            # assign to first table in the from list if only one table, else attempt to find a table that has this column in metadata
            assigned = False
            if len(tables) == 1:
                tbl = tables[0]
                used_cols_by_table.setdefault(tbl, set()).add(col_l)
                assigned = True
            else:
                # try to match by presence in metadata
                for tbl in tables:
                    if tbl in metadata and col_l in metadata[tbl]:
                        used_cols_by_table.setdefault(tbl, set()).add(col_l)
                        assigned = True
                        break
            if not assigned:
                # fallback: record under special key 'unassigned'
                used_cols_by_table.setdefault("__unassigned__", set()).add(col_l)

    # Now compare against declared metadata
    undocumented = []
    for tbl, cols in used_cols_by_table.items():
        if tbl == "__unassigned__":
            for col in cols:
                undocumented.append({"table": None, "column": col, "reason": "column referenced but table not determined"})
            continue
        tbl_l = tbl.lower()
        declared_cols = set(metadata.get(tbl_l, {}).keys()) if tbl_l in metadata else set()
        for col in cols:
            if col not in declared_cols:
                undocumented.append({"table": tbl, "column": col, "reason": "referenced in SQL but not present in metadata"})

    # find declared-but-unused columns
    unused = []
    for tbl, cols in metadata.items():
        for col in cols.keys():
            if tbl not in used_cols_by_table or col not in used_cols_by_table.get(tbl, set()):
                unused.append({"table": tbl, "column": col})

    # inconsistent comments heuristics
    inconsistent = []
    # flag columns marked deprecated/unused in comments but are used
    for tbl, cols in metadata.items():
        for col, info in cols.items():
            comment = (info.get("comment") or "").lower()
            used = tbl in used_cols_by_table and col in used_cols_by_table[tbl]
            # heuristic 1: deprecated but used
            if ("deprecated" in comment or "deprecat" in comment or "should be ignored" in comment) and used:
                inconsistent.append({"table": tbl, "column": col, "comment": info.get("comment"), "reason": "marked deprecated/ignored but appears in SQL"})
            # heuristic 2: comment indicates string but arithmetic usage detected
            if col in arithmetic_cols and ("char" in (info.get("type") or "").lower() or "varchar" in (info.get("type") or "").lower()):
                inconsistent.append({"table": tbl, "column": col, "comment": info.get("comment"), "reason": "column used in arithmetic but declared as string type in metadata"})
            # heuristic 3: comment contains 'legacy' while column is actively transformed
            if "legacy" in comment and used:
                inconsistent.append({"table": tbl, "column": col, "comment": info.get("comment"), "reason": "comment suggests legacy/deprecated but column is actively used/normalized in SQL"})

    return {
        "undocumented_columns": undocumented,
        "unused_metadata_columns": unused,
        "inconsistent_comments": inconsistent,
        "used_columns_by_table": {k: sorted(list(v)) for k, v in used_cols_by_table.items()}
    }

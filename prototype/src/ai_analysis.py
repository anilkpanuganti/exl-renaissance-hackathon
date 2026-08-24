"""
ai_analysis.py
--------------
Phase 2: AI Analysis Layer.

Takes raw legacy SQL and produces a structured JSON extraction of:
  - tables referenced
  - business rules embedded in the logic
  - dependencies between objects

Prompting approach documented in docs/prompt-engineering.md.
"""

import json
from .llm_client import LLMClient

ANALYSIS_SYSTEM_PROMPT = """You are performing legacy code ANALYSIS as part of an
ETL modernization framework (EXTRACT mode).

Your job: read the provided legacy SQL/PLSQL script and extract, as a single
JSON object, the following fields:
  - "tables": list of every table name referenced (source or target)
  - "business_rules": list of objects, each with:
      id, name, description, confidence (0-1)
      Optionally: ambiguity_flag (true/false), confidence_notes (string)
  - "dependencies": list of short strings describing which objects depend on which

STRICT RULES:
1. Only reference tables, columns, and literal values that actually appear in
   the provided script. Never invent an entity.
2. Distinguish "business rules" (thresholds, tiers, discount logic, status
   mapping, filters with business meaning) from plain technical operations
   (type casts, trims, simple renames) - only the former go in business_rules.
3. If a rule's business justification is not documented in the script
   (e.g. an unexplained magic number or date window), set ambiguity_flag=true
   and explain what's unclear in confidence_notes rather than guessing at intent.
4. Think step by step internally (identify tables -> identify joins -> identify
   conditional logic -> name the business rule each conditional implements)
   before producing the final JSON. Output ONLY the final JSON, no reasoning text.

Example (abbreviated):
Input SQL: "CASE WHEN score >= 90 THEN 'A' WHEN score >= 80 THEN 'B' ELSE 'C' END AS grade"
Output: {"tables": [], "business_rules": [{"id": "BR-EX", "name": "Grade Banding",
"description": "Score >=90 -> A, >=80 -> B, else C.", "confidence": 0.95}], "dependencies": []}
"""


def analyze_legacy_sql(sql_text: str, llm_client: LLMClient = None) -> dict:
    """Run the AI Analysis Layer over a legacy SQL script.

    Returns a dict with keys: tables, business_rules, dependencies, _meta
    """
    client = llm_client or LLMClient()
    response = client.complete(ANALYSIS_SYSTEM_PROMPT, sql_text)

    try:
        parsed = json.loads(response.text)
    except json.JSONDecodeError:
        # Defensive: real LLM responses occasionally wrap JSON in prose/fences.
        cleaned = response.text.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        parsed = json.loads(cleaned)

    parsed["_meta"] = {
        "provider": response.provider,
        "model": response.model,
        "layer": "AI Analysis Layer",
    }
    return parsed


if __name__ == "__main__":
    with open("prototype/sample_legacy/legacy_customer_orders_etl.sql") as f:
        sql = f.read()
    result = analyze_legacy_sql(sql)
    print(json.dumps(result, indent=2))

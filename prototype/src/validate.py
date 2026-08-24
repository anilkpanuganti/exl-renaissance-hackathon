"""
validate.py
-----------
Phase 4: Validation Layer.

Implements the hallucination guardrail and the quantitative metrics defined
in docs/evaluation-rubric.md:
  - Business Rule Extraction Coverage
  - Entity Grounding Accuracy
  - SQL Construct Mapping Completeness (basic heuristic for the PoC)
"""

import json
import re


def entity_grounding_accuracy(analysis: dict, source_sql: str) -> dict:
    """Every table/entity the AI claims to have found must actually appear
    in the source SQL text. This is the core hallucination guardrail."""
    tables = analysis.get("tables", [])
    if not tables:
        return {"score": None, "checked": 0, "grounded": 0, "ungrounded": []}

    ungrounded = [t for t in tables if t.lower() not in source_sql.lower()]
    grounded_count = len(tables) - len(ungrounded)
    return {
        "score": round(grounded_count / len(tables), 3),
        "checked": len(tables),
        "grounded": grounded_count,
        "ungrounded": ungrounded,
    }


def business_rule_coverage(analysis: dict, ground_truth: dict) -> dict:
    """Fuzzy-match extracted rule descriptions against hand-annotated ground
    truth rules by keyword overlap. This is a simple heuristic appropriate
    for a PoC (n=1 sample) - not a production NLP similarity metric."""
    gt_rules = ground_truth.get("business_rules", [])
    extracted = analysis.get("business_rules", [])

    extracted_text = " ".join(
        (r.get("name", "") + " " + r.get("description", "")).lower()
        for r in extracted
    )

    matched = []
    missed = []
    for gt in gt_rules:
        keywords = _keywords(gt["name"])
        hit = any(kw in extracted_text for kw in keywords)
        if hit:
            matched.append(gt["id"])
        else:
            missed.append(gt["id"])

    coverage = round(len(matched) / len(gt_rules), 3) if gt_rules else None
    return {
        "score": coverage,
        "total_ground_truth_rules": len(gt_rules),
        "matched": matched,
        "missed": missed,
    }


def _keywords(name: str) -> list:
    stop = {"the", "a", "an", "of", "and", "for", "based", "type"}
    return [w.lower() for w in re.findall(r"[A-Za-z]+", name) if w.lower() not in stop]


def ambiguity_flag_recall(analysis: dict, ground_truth: dict) -> dict:
    """Of the ground-truth rules explicitly marked ambiguous, how many did
    the AI Analysis Layer also flag as ambiguous (rather than silently
    guessing at business intent)? This directly evidences the hallucination
    guardrail described in docs/architecture.md."""
    gt_ambiguous_ids = {r["id"] for r in ground_truth.get("business_rules", [])
                         if r.get("ambiguity_flag")}
    if not gt_ambiguous_ids:
        return {"score": None, "expected": 0, "flagged": 0}

    extracted_flagged = sum(
        1 for r in analysis.get("business_rules", []) if r.get("ambiguity_flag")
    )
    return {
        "score": round(min(extracted_flagged, len(gt_ambiguous_ids)) / len(gt_ambiguous_ids), 3),
        "expected": len(gt_ambiguous_ids),
        "flagged_by_ai": extracted_flagged,
    }


def run_validation(analysis: dict, source_sql: str, ground_truth: dict) -> dict:
    grounding = entity_grounding_accuracy(analysis, source_sql)
    coverage = business_rule_coverage(analysis, ground_truth)
    ambiguity = ambiguity_flag_recall(analysis, ground_truth)

    checks_passed = []
    checks_failed = []

    if grounding["score"] is not None:
        (checks_passed if grounding["score"] >= 0.9 else checks_failed).append(
            f"Entity Grounding Accuracy: {grounding['score']*100:.1f}%"
        )
    if coverage["score"] is not None:
        (checks_passed if coverage["score"] >= 0.7 else checks_failed).append(
            f"Business Rule Extraction Coverage: {coverage['score']*100:.1f}%"
        )
    if ambiguity["score"] is not None:
        (checks_passed if ambiguity["score"] >= 0.5 else checks_failed).append(
            f"Ambiguity Flag Recall: {ambiguity['score']*100:.1f}%"
        )

    return {
        "entity_grounding_accuracy": grounding,
        "business_rule_coverage": coverage,
        "ambiguity_flag_recall": ambiguity,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "overall_status": "PASS" if not checks_failed else "REVIEW_REQUIRED",
    }


if __name__ == "__main__":
    from .ai_analysis import analyze_legacy_sql

    with open("prototype/sample_legacy/legacy_customer_orders_etl.sql") as f:
        sql = f.read()
    with open("prototype/sample_legacy/ground_truth_rules.json") as f:
        gt = json.load(f)

    analysis = analyze_legacy_sql(sql)
    result = run_validation(analysis, sql, gt)
    print(json.dumps(result, indent=2))

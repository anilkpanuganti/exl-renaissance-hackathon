"""
estimator.py
------------
Produce rough cost/time/efficiency estimates for the five key layers of the
pipeline. This is a deterministic heuristic estimator intended for planning
and demo purposes only — not a billing system.

Layers estimated (5):
 - Discovery & Assessment
 - AI Analysis
 - Transformation
 - Validation
 - Documentation / Migration Planning

Produces prototype/output/estimates.json and returns the estimates dict.
"""
from typing import Dict
import json
import os

# Assumptions / knobs
HOURLY_RATE_USD = 80.0  # blended engineering hourly rate for estimates
BASE_DISCOVERY_HOURS = 2.0
PER_TABLE_ANALYSIS_HOURS = 0.25
PER_RULE_REVIEW_HOURS = 0.1
DBT_FILE_GEN_HOURS = 0.05
VALIDATION_PER_CHECK_HOURS = 0.1
DOC_PER_PAGE_HOURS = 0.5


def estimate_cost_time(analysis: Dict, migration_plan: Dict, validation: Dict, output_dir: str) -> Dict:
    """Return deterministic estimates for time (hours) and cost (USD) per layer.

    Uses simple counts from analysis and migration_plan. Also produces an
    overall efficiency estimate relative to a fully manual baseline.
    """
    tables_count = len(analysis.get("tables", []))
    rules_count = len(analysis.get("business_rules", []))
    ambiguous_count = len([r for r in analysis.get("business_rules", []) if r.get("ambiguity_flag")])
    steps_count = len(migration_plan.get("steps", [])) if migration_plan else 0

    # Discovery & Assessment
    discovery_hours = BASE_DISCOVERY_HOURS + 0.1 * tables_count

    # AI Analysis: model + prompt engineering + review
    analysis_hours = PER_TABLE_ANALYSIS_HOURS * tables_count + 0.5 * rules_count

    # Transformation: dbt model generation + minor manual edits
    transform_hours = DBT_FILE_GEN_HOURS * max(1, tables_count) + 0.2 * tables_count

    # Validation: run automated checks + human remedies for failures
    validation_checks = len(validation.get("checks_passed", [])) + len(validation.get("checks_failed", []))
    validation_hours = validation_checks * VALIDATION_PER_CHECK_HOURS + 0.5 * ambiguous_count

    # Documentation / Migration Planning
    docs_hours = DOC_PER_PAGE_HOURS * max(1, int(1 + 0.5 * tables_count)) + 0.25 * steps_count

    total_hours = discovery_hours + analysis_hours + transform_hours + validation_hours + docs_hours
    total_cost = total_hours * HOURLY_RATE_USD

    # Efficiency heuristic: how much manual time this PoC saves vs manual baseline
    # Baseline naive estimate: manual baseline = 3 * (analysis + transform + validation) hours per table
    manual_baseline_hours = 3 * (PER_TABLE_ANALYSIS_HOURS * tables_count + 0.5 * tables_count + 0.5 * tables_count)
    if manual_baseline_hours <= 0:
        efficiency_pct = 0.0
    else:
        efficiency_pct = max(0.0, min(100.0, 100.0 * (manual_baseline_hours - total_hours) / manual_baseline_hours))

    estimates = {
        "layers": {
            "discovery_assessment": {"hours": round(discovery_hours, 2), "cost_usd": round(discovery_hours * HOURLY_RATE_USD, 2)},
            "ai_analysis": {"hours": round(analysis_hours, 2), "cost_usd": round(analysis_hours * HOURLY_RATE_USD, 2)},
            "transformation": {"hours": round(transform_hours, 2), "cost_usd": round(transform_hours * HOURLY_RATE_USD, 2)},
            "validation": {"hours": round(validation_hours, 2), "cost_usd": round(validation_hours * HOURLY_RATE_USD, 2)},
            "documentation_planning": {"hours": round(docs_hours, 2), "cost_usd": round(docs_hours * HOURLY_RATE_USD, 2)},
        },
        "summary": {
            "total_hours": round(total_hours, 2),
            "total_cost_usd": round(total_cost, 2),
            "estimated_efficiency_pct": round(efficiency_pct, 1),
            "assumptions": {
                "hourly_rate_usd": HOURLY_RATE_USD,
                "note": "Heuristic estimates for planning/demos only — verify with real team data."
            }
        },
        "counts": {"tables": tables_count, "business_rules": rules_count, "ambiguous_rules": ambiguous_count, "migration_steps": steps_count}
    }

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "estimates.json")
    with open(out_path, "w") as f:
        json.dump(estimates, f, indent=2)

    return {"path": out_path, "estimates": estimates}

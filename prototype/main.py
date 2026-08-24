"""
main.py
-------
Orchestrates the full GenAI-Assisted Modernization PoC pipeline:

  Phase 2: AI Analysis        -> src/ai_analysis.py
  Phase 3: Transformation     -> src/transform.py
  [Human-in-the-loop checkpoint - simulated]
  Phase 4: Validation         -> src/validate.py
  Phase 5: Documentation      -> src/generate_docs.py

Run with:
    python -m prototype.main

No API key required - runs in mock mode by default. Set ANTHROPIC_API_KEY
or OPENAI_API_KEY to use a real LLM for the analysis/transformation steps.
"""

import json
import os
import sys

from src.ai_analysis import analyze_legacy_sql
from src.transform import generate_dbt_models
from src.validate import run_validation
from src.generate_docs import generate_migration_report
from src.llm_client import LLMClient

SAMPLE_SQL_PATH = "sample_legacy/legacy_customer_orders_etl.sql"
GROUND_TRUTH_PATH = "sample_legacy/ground_truth_rules.json"
OUTPUT_DIR = "output"


def human_checkpoint(analysis: dict) -> None:
    """Simulated human-in-the-loop review gate (see docs/architecture.md).

    In this PoC this is a printed checkpoint rather than an interactive
    prompt, so the pipeline remains scriptable/demoable end-to-end. In a
    real deployment this would pause for actual developer sign-off before
    proceeding to Validation.
    """
    ambiguous = [r for r in analysis.get("business_rules", []) if r.get("ambiguity_flag")]
    print("\n--- HUMAN-IN-THE-LOOP CHECKPOINT (simulated) ---")
    if ambiguous:
        print(f"{len(ambiguous)} rule(s) flagged for mandatory human review before proceeding:")
        for r in ambiguous:
            print(f"  - {r.get('id')}: {r.get('name')} -> {r.get('confidence_notes')}")
    else:
        print("No rules flagged as ambiguous by the AI Analysis Layer.")
    print("[Simulated approval granted - proceeding to Validation Layer]\n")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(SAMPLE_SQL_PATH) as f:
        sql_text = f.read()
    with open(GROUND_TRUTH_PATH) as f:
        ground_truth = json.load(f)

    client = LLMClient()
    print(f"Running pipeline with provider: {client.provider} (model: {client.model})")
    if client.provider == "mock":
        print("NOTE: No ANTHROPIC_API_KEY or OPENAI_API_KEY found - running in "
              "mock mode. Full pipeline logic still executes end-to-end.\n")

    # Phase 2: AI Analysis
    print("--- Phase 2: AI Analysis Layer ---")
    analysis = analyze_legacy_sql(sql_text, client)
    with open(os.path.join(OUTPUT_DIR, "analysis.json"), "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"Extracted {len(analysis.get('tables', []))} tables, "
          f"{len(analysis.get('business_rules', []))} business rules.\n")

    # Phase 3: Transformation
    print("--- Phase 3: Transformation Layer ---")
    dbt_files = generate_dbt_models(analysis, OUTPUT_DIR)
    print(f"Generated {len(dbt_files)} dbt/Snowflake artifact files.\n")

    # Human-in-the-loop checkpoint
    human_checkpoint(analysis)

    # Phase 4: Validation
    print("--- Phase 4: Validation Layer ---")
    validation = run_validation(analysis, sql_text, ground_truth)
    with open(os.path.join(OUTPUT_DIR, "validation_report.json"), "w") as f:
        json.dump(validation, f, indent=2)
    print(f"Validation status: {validation['overall_status']}")
    for c in validation["checks_passed"]:
        print(f"  PASS: {c}")
    for c in validation["checks_failed"]:
        print(f"  ATTENTION: {c}")
    print()

    # Phase 5: Documentation
    print("--- Phase 5: Output Layer (Documentation) ---")
    report = generate_migration_report(
        analysis, validation, dbt_files, source_name="legacy_customer_orders_etl.sql"
    )
    report_path = os.path.join(OUTPUT_DIR, "migration_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Migration report written to {report_path}\n")

    print("Pipeline complete. See prototype/output/ for all artifacts.")


if __name__ == "__main__":
    sys.exit(main())

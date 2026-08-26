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
import argparse

from src.ai_analysis import analyze_legacy_sql
from src.transform import generate_dbt_models
from src.validate import run_validation
from src.generate_docs import generate_migration_report
from src.llm_client import LLMClient
from src.metadata_interpreter import interpret_metadata

SAMPLE_SQL_PATH = "sample_legacy/legacy_customer_orders_etl.sql"
GROUND_TRUTH_PATH = "sample_legacy/ground_truth_rules.json"
OUTPUT_DIR = "output"


def human_checkpoint(analysis: dict, auto_approve: bool = False) -> None:
    """Human-in-the-loop review gate.

    If auto_approve is True, behaves non-interactively (CI-friendly).
    Otherwise prompts the reviewer for each ambiguous rule with options:
      [a]pprove as-is, [e]dit description, [r]eject and halt pipeline.

    Edited descriptions update the in-memory analysis dict so subsequent
    Validation runs use the reviewer-updated text.
    """
    ambiguous = [r for r in analysis.get("business_rules", []) if r.get("ambiguity_flag")]
    print("\n--- HUMAN-IN-THE-LOOP CHECKPOINT ---")
    if not ambiguous:
        print("No rules flagged as ambiguous by the AI Analysis Layer.")
        print("Proceeding to Validation Layer.\n")
        return

    print(f"{len(ambiguous)} rule(s) flagged for mandatory human review before proceeding:")

    if auto_approve:
        # Preserve existing non-interactive / CI behavior
        for r in ambiguous:
            print(f"  - Auto-approved: {r.get('id')}: {r.get('name')} -> {r.get('confidence_notes')}")
        print("[Auto-approve enabled - proceeding to Validation Layer]\n")
        return

    # Interactive review loop
    for r in ambiguous:
        rid = r.get("id")
        name = r.get("name")
        desc = r.get("description", "(no description)")
        notes = r.get("confidence_notes", "")
        print("\n----------------------------------------")
        print(f"Rule ID: {rid}")
        print(f"Name   : {name}")
        print(f"Current: {desc}")
        if notes:
            print(f"Notes  : {notes}")

        while True:
            print("Choose action: [a]pprove as-is, [e]dit description, [r]eject and halt pipeline")
            choice = input("Action (a/e/r): ").strip().lower()
            if choice == "a":
                print(f"Approved rule {rid} as-is.")
                break
            elif choice == "e":
                new_desc = input("Enter new rule description: ").strip()
                if new_desc:
                    r["description"] = new_desc
                    print(f"Updated rule {rid} description.")
                    break
                else:
                    print("Empty description; please enter a non-empty value or choose another action.")
            elif choice == "r":
                print(f"Reviewer rejected rule {rid}. Halting pipeline.")
                sys.exit(1)
            else:
                print("Unrecognized choice. Please enter 'a', 'e' or 'r'.")

    print("\nAll ambiguous rules reviewed. Proceeding to Validation Layer.\n")


def main():
    parser = argparse.ArgumentParser(description="Run the PoC pipeline")
    parser.add_argument("--auto-approve", action="store_true",
                        help="Non-interactive: auto-approve ambiguous rules (CI-friendly)")
    parser.add_argument("--target", default=None,
                        help="Path to a single SQL file (default) or a workflow folder containing a manifest.json")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Determine target: default single SQL file for backward compatibility
    target = args.target or SAMPLE_SQL_PATH

    # If target is a directory, expect a manifest.json that lists job scripts
    workflow_jobs = None
    combined_sql_text = ""
    if os.path.isdir(target):
        manifest_path = os.path.join(target, "manifest.json")
        try:
            with open(manifest_path) as mf:
                manifest = json.load(mf)
            workflow_jobs = []
            aggregate_analysis = {"tables": [], "business_rules": [], "dependencies": [], "_meta": {}}
            print(f"Running in workflow mode against folder: {target}")
            client = LLMClient()
            print(f"Running pipeline with provider: {client.provider} (model: {client.model})")
            if client.provider == "mock":
                print("NOTE: No ANTHROPIC_API_KEY or OPENAI_API_KEY found - running in mock mode.\n")
            # Analyze each job in manifest order
            for job in manifest.get("jobs", []):
                job_id = job.get("id")
                job_name = job.get("name")
                script_path = os.path.join(target, job.get("script"))
                try:
                    with open(script_path) as js:
                        job_sql = js.read()
                except FileNotFoundError:
                    print(f"Warning: script {script_path} not found; skipping job {job_id}")
                    continue
                print(f"--- Phase 2: AI Analysis Layer (job: {job_id}) ---")
                job_analysis = analyze_legacy_sql(job_sql, client)
                # write per-job analysis file
                with open(os.path.join(OUTPUT_DIR, f"analysis_{job_id}.json"), "w") as f:
                    json.dump(job_analysis, f, indent=2)
                workflow_jobs.append({"id": job_id, "name": job_name, "analysis": job_analysis})
                # merge into aggregate
                aggregate_analysis["tables"].extend([t for t in job_analysis.get("tables", []) if t not in aggregate_analysis["tables"]])
                aggregate_analysis["business_rules"].extend(job_analysis.get("business_rules", []))
                aggregate_analysis["dependencies"].extend(job_analysis.get("dependencies", []))
                # accumulate SQL for downstream steps
                combined_sql_text += f"\n-- JOB: {job_id} --\n" + job_sql
            # final analysis is aggregate_analysis
            analysis = aggregate_analysis
            analysis["_meta"] = {"provider": client.provider, "model": client.model}
            # try to load workflow-specific ground truth if present
            gt_path = os.path.join(target, "ground_truth_rules.json")
            try:
                with open(gt_path) as gf:
                    ground_truth = json.load(gf)
            except FileNotFoundError:
                ground_truth = {"description": "No ground truth provided for workflow; validation will run limited checks."}
        except FileNotFoundError:
            print(f"manifest.json not found in {target}; falling back to single-file mode.")
            with open(SAMPLE_SQL_PATH) as f:
                combined_sql_text = f.read()
            with open(GROUND_TRUTH_PATH) as f:
                ground_truth = json.load(f)
            client = LLMClient()
            print(f"Running pipeline with provider: {client.provider} (model: {client.model})")
            if client.provider == "mock":
                print("NOTE: No ANTHROPIC_API_KEY or OPENAI_API_KEY found - running in mock mode. Full pipeline logic still executes end-to-end.\n")
            # Phase 2: AI Analysis
            print("--- Phase 2: AI Analysis Layer ---")
            analysis = analyze_legacy_sql(combined_sql_text, client)
            with open(os.path.join(OUTPUT_DIR, "analysis.json"), "w") as f:
                json.dump(analysis, f, indent=2)
    else:
        # single-file default behavior
        with open(target) as f:
            combined_sql_text = f.read()
        with open(GROUND_TRUTH_PATH) as f:
            ground_truth = json.load(f)
        client = LLMClient()
        print(f"Running pipeline with provider: {client.provider} (model: {client.model})")
        if client.provider == "mock":
            print("NOTE: No ANTHROPIC_API_KEY or OPENAI_API_KEY found - running in mock mode. Full pipeline logic still executes end-to-end.\n")
        # Phase 2: AI Analysis
        print("--- Phase 2: AI Analysis Layer ---")
        analysis = analyze_legacy_sql(combined_sql_text, client)
        with open(os.path.join(OUTPUT_DIR, "analysis.json"), "w") as f:
            json.dump(analysis, f, indent=2)

    # At this point: analysis (aggregate or single), combined_sql_text, workflow_jobs (None or list)

    print(f"Extracted {len(analysis.get('tables', []))} tables, "
          f"{len(analysis.get('business_rules', []))} business rules.\n")

    # Phase 3a: Metadata interpretation (cross-reference declared metadata)
    print("--- Phase 3a: Metadata Interpretation ---")
    metadata_path = "sample_legacy/legacy_metadata.json"
    metadata_findings = {}
    try:
        with open(metadata_path) as mf:
            metadata_json = json.load(mf)
        metadata_findings = interpret_metadata(metadata_json, combined_sql_text)
        with open(os.path.join(OUTPUT_DIR, "metadata_interpretation.json"), "w") as f:
            json.dump(metadata_findings, f, indent=2)
        print(f"Metadata interpretation written to {os.path.join(OUTPUT_DIR, 'metadata_interpretation.json')}\n")
    except FileNotFoundError:
        print(f"No metadata file found at {metadata_path}; skipping metadata interpretation.\n")

    # Phase 3: Transformation
    print("--- Phase 3: Transformation Layer ---")
    dbt_files = generate_dbt_models(analysis, OUTPUT_DIR)
    print(f"Generated {len(dbt_files)} dbt/Snowflake artifact files.\n")

    # Human-in-the-loop checkpoint (interactive unless --auto-approve)
    human_checkpoint(analysis, auto_approve=args.auto_approve)

    # Phase 4: Validation
    print("--- Phase 4: Validation Layer ---")
    validation = run_validation(analysis, combined_sql_text, ground_truth)
    with open(os.path.join(OUTPUT_DIR, "validation_report.json"), "w") as f:
        json.dump(validation, f, indent=2)
    print(f"Validation status: {validation['overall_status']}")
    for c in validation["checks_passed"]:
        print(f"  PASS: {c}")
    for c in validation["checks_failed"]:
        print(f"  ATTENTION: {c}")
    print()

    # Phase 5: Migration Planning (generate deterministic plan)
    from src.migration_planner import generate_migration_plan
    print("--- Phase 5: Migration Planning ---")
    migration_plan = generate_migration_plan(analysis, validation)
    with open(os.path.join(OUTPUT_DIR, "migration_plan.json"), "w") as f:
        json.dump(migration_plan, f, indent=2)
    print(f"Migration plan written to {os.path.join(OUTPUT_DIR, 'migration_plan.json')}\n")

    # Generate lineage artifacts (DOT/JSON/mermaid) for visualization
    try:
        from src.lineage import generate_lineage_graph
        print("--- Lineage: generating lineage artifacts ---")
        lineage_files = generate_lineage_graph(analysis, OUTPUT_DIR, metadata_findings)
        print(f"Lineage artifacts written: {lineage_files.get('json')}, {lineage_files.get('dot')}")
    except Exception as e:
        print(f"Lineage generation failed: {e}")
        lineage_files = None

    # Produce cost/time/efficiency estimates for the 5-layer workflow
    try:
        from src.estimator import estimate_cost_time
        print("--- Estimator: computing cost/time/efficiency estimates ---")
        estimates_result = estimate_cost_time(analysis, migration_plan, validation, OUTPUT_DIR)
        estimates = estimates_result.get('estimates')
        print(f"Estimates written to: {estimates_result.get('path')}")
    except Exception as e:
        print(f"Estimation failed: {e}")
        estimates = None

    # Phase 6: Documentation
    print("--- Phase 6: Output Layer (Documentation) ---")
    report = generate_migration_report(
        analysis, validation, dbt_files, source_name=(target if args.target else "legacy_customer_orders_etl.sql"),
        metadata_findings=metadata_findings,
        workflow_jobs=workflow_jobs,
        migration_plan=migration_plan,
        estimates=estimates,
        lineage_files=lineage_files
    )
    report_path = os.path.join(OUTPUT_DIR, "migration_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Migration report written to {report_path}\n")

    print("Pipeline complete. See prototype/output/ for all artifacts.")


if __name__ == "__main__":
    sys.exit(main())

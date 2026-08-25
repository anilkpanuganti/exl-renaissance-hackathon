"""
generate_docs.py
-----------------
Phase 5: Output Layer - migration report generation.

Assembles the AI Analysis, Transformation, and Validation outputs into a
single human-readable migration_report.md, matching the documentation
deliverables described in the project outline (mapping documents, migration
reports, transformation descriptions, data lineage explanations).
"""

from datetime import datetime, timezone


def generate_migration_report(analysis: dict, validation: dict, dbt_files: list,
                               source_name: str, metadata_findings: dict = None,
                               workflow_jobs: list = None,
                               migration_plan: dict = None) -> str:
    lines = []
    lines.append(f"# Migration Report: {source_name}")
    lines.append("")
    lines.append(f"_Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_")
    lines.append(f"_AI Provider: {analysis.get('_meta', {}).get('provider', 'unknown')} "
                 f"/ Model: {analysis.get('_meta', {}).get('model', 'unknown')}_")
    lines.append("")
    lines.append("> ⚠️ **This report is AI-generated and has NOT yet passed human "
                 "review.** Per the framework's human-in-the-loop checkpoint "
                 "(see docs/architecture.md), a developer must review flagged "
                 "items below before this migration is considered approved.")
    lines.append("")

    # --- Overview ---
    lines.append("## 1. Overview")
    lines.append("")
    lines.append(f"- **Tables involved:** {', '.join(analysis.get('tables', [])) or 'none detected'}")
    lines.append(f"- **Business rules identified:** {len(analysis.get('business_rules', []))}")
    ambiguous = [r for r in analysis.get('business_rules', []) if r.get('ambiguity_flag')]
    lines.append(f"- **Rules flagged for human review (ambiguous):** {len(ambiguous)}")
    lines.append(f"- **Validation status:** {validation.get('overall_status', 'unknown')}")
    lines.append("")

    # --- Business Rule Mapping Table ---
    lines.append("## 2. Business Rule → Snowflake/dbt Mapping")
    lines.append("")
    lines.append("| ID | Rule | Description | Confidence | Needs Review |")
    lines.append("|---|---|---|---|---|")
    for r in analysis.get("business_rules", []):
        review = "⚠️ YES" if r.get("ambiguity_flag") else "No"
        lines.append(
            f"| {r.get('id','')} | {r.get('name','')} | {r.get('description','')} "
            f"| {r.get('confidence','n/a')} | {review} |"
        )
    lines.append("")

    if ambiguous:
        lines.append("### Ambiguous Rules Requiring Human Sign-off")
        lines.append("")
        for r in ambiguous:
            lines.append(f"- **{r.get('id')} — {r.get('name')}**: "
                          f"{r.get('confidence_notes', 'No business justification found in source.')}")
        lines.append("")

    # --- Dependencies / Lineage ---
    lines.append("## 3. Data Lineage / Dependencies")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart LR")
    for dep in analysis.get("dependencies", []):
        if " depends on " in dep:
            child, parents = dep.split(" depends on ")
            for parent in parents.split(","):
                lines.append(f"    {parent.strip().replace(' ', '_')} --> {child.strip().replace(' ', '_')}")
    lines.append("```")
    lines.append("")

    # --- Generated Artifacts ---
    lines.append("## 4. Generated dbt/Snowflake Artifacts")
    lines.append("")
    for f in dbt_files:
        lines.append(f"- `{f}`")
    lines.append("")

    # --- Per-job breakdown (workflow) ---
    if workflow_jobs:
        lines.append("## 4.a Per‑job Analysis")
        lines.append("")
        for job in workflow_jobs:
            job_id = job.get('id')
            job_name = job.get('name')
            job_analysis = job.get('analysis', {})
            lines.append(f"### Job: {job_id} — {job_name}")
            lines.append("")
            lines.append(f"- Tables detected: {', '.join(job_analysis.get('tables', [])) or 'none'}")
            lines.append(f"- Business rules identified: {len(job_analysis.get('business_rules', []))}")
            ambiguous = [r for r in job_analysis.get('business_rules', []) if r.get('ambiguity_flag')]
            lines.append(f"- Rules flagged ambiguous: {len(ambiguous)}")
            lines.append("")
    # --- Validation Summary ---
    lines.append("## 5. Validation Summary")
    lines.append("")
    lines.append(f"**Overall status:** {validation.get('overall_status')}")
    lines.append("")
    lines.append("**Checks passed:**")
    for c in validation.get("checks_passed", []):
        lines.append(f"- ✅ {c}")
    lines.append("")
    lines.append("**Checks requiring attention:**")
    for c in validation.get("checks_failed", []):
        lines.append(f"- ⚠️ {c}")
    if not validation.get("checks_failed"):
        lines.append("- None")
    lines.append("")

    grounding = validation.get("entity_grounding_accuracy", {})
    if grounding.get("ungrounded"):
        lines.append(f"**Ungrounded entities detected (possible hallucination):** "
                      f"{', '.join(grounding['ungrounded'])}")
        lines.append("")

    # --- Metadata Interpretation Findings ---
    if metadata_findings:
        lines.append("## Metadata Interpretation Findings")
        lines.append("")
        undocumented = metadata_findings.get('undocumented_columns', [])
        unused = metadata_findings.get('unused_metadata_columns', [])
        inconsistent = metadata_findings.get('inconsistent_comments', [])

        lines.append("### Undocumented columns referenced in SQL")
        if undocumented:
            for u in undocumented:
                tbl = u.get('table') or '(unknown)'
                lines.append(f"- {tbl}.{u.get('column')}: {u.get('reason')}")
        else:
            lines.append("- None detected")
        lines.append("")

        lines.append("### Declared metadata columns not used by the SQL (potential dead columns)")
        if unused:
            for u in unused:
                lines.append(f"- {u.get('table')}.{u.get('column')}")
        else:
            lines.append("- None detected")
        lines.append("")

        lines.append("### Inconsistent or suspicious column comments")
        if inconsistent:
            for inc in inconsistent:
                lines.append(f"- {inc.get('table')}.{inc.get('column')}: {inc.get('reason')} -- comment: {inc.get('comment')}")
        else:
            lines.append("- None detected")
        lines.append("")

    # --- Migration Plan ---
    if migration_plan:
        lines.append("## Migration Plan")
        lines.append("")
        lines.append("| Order | Table | Effort | Blocking | Rules touching |")
        lines.append("|---|---|---|---|---|")
        for step in migration_plan.get('steps', []):
            rules = ", ".join(step.get('rules_touching', [])) or '-' 
            lines.append(f"| {step.get('order')} | {step.get('table')} | {step.get('effort')} | {str(step.get('blocking'))} | {rules} |")
        lines.append("")

    lines.append("## 6. Recommendation")
    lines.append("")
    if validation.get("overall_status") == "PASS":
        lines.append("All automated checks passed. Recommend proceeding to human "
                      "review of flagged ambiguous rules, then promotion to the "
                      "Snowflake target environment.")
    else:
        lines.append("One or more automated checks require attention before this "
                      "migration proceeds. See Section 5.")
    lines.append("")

    return "\n".join(lines)

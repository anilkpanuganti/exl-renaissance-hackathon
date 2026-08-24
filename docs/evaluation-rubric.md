# PoC Evaluation Rubric

The project outline calls for "qualitative evaluation" of the framework. To
meet market standards, the PoC also reports **quantitative** metrics computed
directly from its own run, so the evaluation isn't purely subjective.

## 1. Metrics Computed by the PoC (`prototype/src/validate.py`)

| Metric | Definition | Why it matters |
|---|---|---|
| **Business Rule Extraction Coverage** | % of manually-annotated business rules in the sample script that the AI Analysis Layer also identified | Directly measures the core value proposition (rule extraction) |
| **Entity Grounding Accuracy** | % of tables/columns referenced in AI output that actually exist in the source script | Hallucination guardrail metric |
| **SQL Construct Mapping Completeness** | % of legacy SQL constructs (joins, case-when blocks, subqueries) with a corresponding Snowflake/dbt equivalent generated | Measures transformation completeness |
| **Documentation Completeness Score** | Presence/absence of required sections in the generated migration report (lineage, mapping table, business rules, risks) | Ties back to Objective 5 (documentation quality) |
| **Estimated Manual-Effort Reduction** | (Estimated manual analysis hours for the sample script) vs (time to run PoC + human review) | Rough productivity signal — explicitly labeled as an estimate, not a benchmark |

## 2. Qualitative Evaluation Criteria (from the project outline)

- Ease of adoption
- Documentation completeness
- Governance support
- Maintainability
- Migration consistency
- Expected productivity improvements

## 3. Scoring Approach

Each PoC run produces a `validation_report.md` with:
- A pass/fail per rule-based check
- The four quantitative metrics above, computed against the one hand-annotated
  sample (`prototype/sample_legacy/legacy_customer_orders_etl.sql` +
  `prototype/sample_legacy/ground_truth_rules.json`)
- An explicit statement of sample size (n=1 sample pipeline) and the
  limitation that this is illustrative, not a statistically validated
  benchmark — consistent with the project's stated PoC scope (feasibility,
  not production performance benchmarking).

## 4. What "Good" Looks Like for the Hackathon Demo

- Extraction coverage and grounding accuracy both reported >80% on the sample
- At least one deliberately-injected ambiguous rule in the sample script that
  the model correctly flags via `confidence_notes` rather than guessing
  (demonstrates the hallucination guardrail actually works, not just claims to)
- A clear, reviewable diff between legacy SQL and generated dbt models

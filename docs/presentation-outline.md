Slide 1 — Title

- GenAI-Assisted Framework for Modernizing Legacy ETL → Snowflake (EXL PoC)
- Team / Authors: PoC code and docs in prototype/ and docs/
- One-line: Automated discovery → dbt scaffolds → validated migration reports


Slide 2 — Problem: Legacy ETL Pain Points

- Complex workflow dependencies, proprietary platform idioms, and sparse comments (see docs/legacy-etl-challenges-analysis.md)
- Tribal knowledge: undocumented rules (e.g., 90-day aging discount, 24‑month order window in prototype/sample_legacy/legacy_customer_orders_etl.sql)
- High maintenance cost and low testability; no version/meta history in sample assets


Slide 3 — Motivation & Objectives

- Reduce manual analysis time, improve documentation, and lower migration risk (docs/project-outline-source.md Objective 1–5)
- Objectives implemented in PoC: rule extraction, dbt generation, validation metrics, migration planning (see prototype/src/ and docs/PROJECT_REPORT.md)
- Business-focused goals: governance, time-to-market, standardized artifacts


Slide 4 — Framework Overview (Layered)

- Layers: Input → AI Analysis → Transformation → Human-in-the-Loop → Validation → Documentation/Output (see docs/architecture.md)
- Metadata Repository, Monitoring Components, Security Layer sit alongside transformation
- Human checkpoint enforces review of ambiguity-flagged rules before promotion


Slide 5 — Snowflake Capabilities Mapped to Framework

- Separation of compute/storage → Transformation & Staging layers (docs/snowflake-capabilities-study.md)
- Zero-copy cloning & Time Travel → Validation Layer rollback/testing strategy
- Data sharing, RBAC, masking → Output & Security Layer for governance


Slide 6 — PoC Architecture & Code Walkthrough

- Provider-agnostic LLM client with mock, Anthropic, OpenAI modes (prototype/src/llm_client.py)
- AI Analysis: prototype/src/ai_analysis.py → produces analysis.json
- Transformation: prototype/src/transform.py → generates dbt_models/ files
- Metadata interpreter & migration planner: prototype/src/metadata_interpreter.py and migration_planner.py


Slide 7 — Live Demo Walkthrough (What you'll see)

- Run: cd prototype && python main.py --auto-approve (mock mode by default)
- Outputs to show: prototype/output/migration_report.md, prototype/output/validation_report.json, prototype/output/dbt_models/, prototype/output/migration_plan.json
- Demo assets: single-script legacy_customer_orders_etl.sql and multi-job workflow_inventory_sync manifest + job SQLs


Slide 8 — Validation Results (Actual PoC metrics)

- PoC metrics (docs/evaluation-rubric.md): Entity Grounding Accuracy, Business Rule Extraction Coverage, Ambiguity Flag Recall
- Example run (mock): migration_report.md shows Overall status: PASS with 100% grounding, 100% coverage, 100% ambiguity recall for the primary sample
- Workflow sample: demonstrated per-job breakdown and showed REVIEW_REQUIRED where coverage was low (see prototype/output/ migration_report.md for workflow run)


Slide 9 — Business Benefits (Evidence-backed)

- Productivity: automated extraction + dbt scaffolds reduce initial analysis effort (see docs/business-benefits-evaluation.md)
- Governance & risk reduction: ambiguity flags, validation checks, metadata interpretation (prototype/output/metadata_interpretation.json) support reviewable audit trails
- Standardization & knowledge capture: generated migration_report.md and metadata repository artifacts


Slide 10 — Limitations & Risks

- Sample size: n=1 primary demo + one workflow sample; metrics illustrative, not production benchmarks (docs/evaluation-rubric.md)
- LLM variability and prompt/parsing sensitivity — guidance and parsing fallback discussed in docs/prompt-engineering.md and ai_analysis.py
- Snowflake edition/account specifics (Time Travel and cloning retention) need validation per customer (docs/snowflake-capabilities-study.md)


Slide 11 — Next Steps / Roadmap

- Run pipeline across a larger corpus to measure real productivity and tune prompts
- Harden parsing for real LLM outputs; integrate with a Snowflake sandbox for clone/time-travel validation
- Integrate with CI/CD and customer RBAC/tagging standards; add more tests and provenance artifacts (docs/PROJECT_REPORT.md recommendations)


Slide 12 — Q&A / Contact

- Where to find the code & artifacts: prototype/ and docs/
- Example outputs: prototype/output/migration_report.md, migration_plan.json, metadata_interpretation.json
- Questions, feedback, collaboration invites

# Legacy ETL Challenges — Analysis with Concrete Examples

This document synthesizes legacy ETL challenges identified in the project requirement (see docs/project-outline-source.md Sections 1–3 and Objective 1) and ties each challenge to concrete evidence from the sample legacy procedure: prototype/sample_legacy/legacy_customer_orders_etl.sql. The goal is an evidence-driven, structured view of risk and how the proposed GenAI-assisted framework addresses each issue.

---

## Summary of the sample asset

The sample is an Oracle PL/SQL stored procedure, sp_load_customer_orders, containing an end-to-end job that: deduplicates staging customers, populates staging orders with embedded business logic, loads a fact table, and performs a SCD-1 merge into dim_customers. Header and inline comments are sparse; source author and modification history are unknown.

Key sample artifacts used below:

- Top-of-file metadata: "Original platform: Oracle PL/SQL" and "Original author: unknown" (header comments)
- Dedupe step using ROWID and a correlated MAX(ROWID)
- Hardcoded customer tier thresholds (lifetime_value >= 50000, >=15000, >=2000)
- Embedded discount logic with an undocumented "aging discount" (extra 2% when (SYSDATE - o.order_date) > 90)
- WHERE o.order_date >= ADD_MONTHS(SYSDATE, -24) — implicit 24-month window
- MERGE into dim_customers implementing SCD type 1 (overwrite, no history)
- Generic exception handler: WHEN OTHERS THEN ROLLBACK; RAISE;

---

## 1. Complex workflow dependencies

Synthesis

- Legacy logic is packaged as a monolithic stored procedure that encodes multiple dependent steps and implicit ordering (dedupe → staging inserts → fact load → dimension merge → COMMIT). There is no explicit DAG metadata, scheduling tags, nor checkpoint state preservation.

Concrete example(s) from sample

- The procedure executes serially in blocks (dedupe, insert stg_customers, insert stg_orders, insert fct_orders, MERGE dim_customers) inside one procedure body — sequencing is implicit and enforced by the code order.

Why this is a problem (business impact)

- Hard to parallelize, test, or resume individual steps. A failure in a mid-step (e.g., during fact load) requires rerunning or manual recovery of earlier steps.

How the framework helps (reference)

- AI Analysis Layer (dependency discovery) extracts step boundaries and dependencies; Transformation Layer maps steps to modular dbt models/tasks; Validation Layer provides idempotent checks and checkpointing to support restartable execution.

---

## 2. Proprietary / platform-specific implementation

Synthesis

- The code is Oracle PL/SQL specific (ROWID, SYSDATE, ADD_MONTHS, PL/SQL exception handling), coupling business logic to a runtime and making direct portability to Snowflake non-trivial.

Concrete example(s) from sample

- File header: "Original platform: Oracle PL/SQL". Uses constructs such as ROWID and SYSDATE and CREATE OR REPLACE PROCEDURE ... AS / BEGIN ... END.

Why this is a problem (business impact)

- Migration requires rewriting platform-specific constructs and validating semantic parity (date arithmetic, ROWID behavior, MERGE semantics). Risk of subtle behavior divergences.

How the framework helps (reference)

- Input Layer (legacy artifacts) + AI Analysis Layer (code understanding & transformation recommendation) identify platform idioms and propose Snowflake-equivalent SQL/dbt patterns in the Transformation Layer. Human-in-the-Loop ensures correctness before deployment.

---

## 3. Incomplete and inconsistent documentation

Synthesis

- Comments are explicit about being "sparse and inconsistent." Important business rules are embedded in code rather than documented in metadata or mapping tables.

Concrete example(s) from sample

- Header: "Original author: unknown (tribal knowledge, not documented)" and inline comment: "tier logic hardcoded, no doc on why these thresholds". The aging discount is noted only inside a CASE comment: "(undocumented business exception, found only in this CASE block)".

Why this is a problem (business impact)

- Onboarding new engineers, auditing, and reproducing past decisions are expensive and error-prone; unclear rules can cause incorrect migration or incorrect analytic results post-migration.

How the framework helps (reference)

- AI Analysis Layer (business rule extraction) surfaces hidden rules into the Metadata Repository; Documentation Generation produces explicit mapping documents and lineage for the Validation and Output Layers.

---

## 4. High maintenance effort

Synthesis

- The procedure uses hardcoded thresholds, magic strings for statuses, and procedural mutating logic (DELETE using ROWID), making small changes invasive and risky across multiple places.

Concrete example(s) from sample

- Customer tier thresholds are hardcoded (50000, 15000, 2000). Order status mapping uses repeated magic strings: WHEN o.order_status IN ('CANC', 'CANCELLED') THEN 'CANCELLED', etc. Dedupe uses ROWID-based deletion logic.

Why this is a problem (business impact)

- Frequent, error-prone edits; regression risk; longer change cycles and higher operational costs.

How the framework helps (reference)

- Transformation Layer converts hardcoded logic into parameterized dbt models or configuration-driven rules; Monitoring Components and Validation Layer add automated tests to detect regressions.

---

## 5. Technical debt (lack of testability, auditability)

Synthesis

- The asset lacks version metadata, structured error logging, and preserves no history (SCD-1). Exception handling is generic and offers no diagnostics.

Concrete example(s) from sample

- Header: "Last known modification: unknown (no version history retained)". MERGE implements SCD type 1 (overwrite), and the exception block uses: "WHEN OTHERS THEN ROLLBACK; RAISE;" with no logging.

Why this is a problem (business impact)

- Difficult to trace when/why data changed; limited ability to audit or rollback; higher compliance risk; debugging failures is slower.

How the framework helps (reference)

- Metadata Repository captures extracted artifacts and versioned AI-generated mappings; Validation Layer introduces test suites and audit artifacts; Time Travel and Zero-copy cloning in the Snowflake Target Architecture enable non-destructive testing and rollback strategies.

---

## 6. Knowledge dependency on senior developers / tribal knowledge

Synthesis

- Implicit business rules exist only in code or in the heads of unknown maintainers (e.g., why 24-month filter or specific tier thresholds). This concentrates risk in people rather than artifacts.

Concrete example(s) from sample

- The WHERE clause restricts orders: "WHERE o.order_date >= ADD_MONTHS(SYSDATE, -24); -- only last 2 years, reason unclear". The aging-discount comment notes the rule was found only in the CASE block (undocumented exception).

Why this is a problem (business impact)

- Single points of failure for institutional knowledge; maintenance and validation require reaching out to rare subject-matter experts.

How the framework helps (reference)

- AI Analysis Layer extracts and summarizes business rules; Documentation Generation and the Metadata Repository externalize tribal knowledge; Human-in-the-Loop Checkpoint validates extracted rules with domain experts before committing changes.

---

## Challenge → Business Impact → How This Framework Addresses It (Quick Table)

| Challenge | Business Impact | How This Framework Addresses It (primary layer) |
|---|---|---|
| Complex workflow dependencies | Hard to test/parallelize; brittle reruns; longer downtime | AI Analysis (dependency discovery) → Transformation Layer (modularize into dbt models/tasks); Validation Layer (checkpointing) |
| Proprietary platform (Oracle PL/SQL) | Portability risk; semantic mismatch during migration | Input Layer (capture artifact) + AI Analysis (translation guidance) → Transformation Layer (dbt/Snowflake mapping) |
| Incomplete documentation | Slow onboarding; misinterpretation of business rules | AI Analysis (business rule extraction) → Metadata Repository; Documentation Generation (Output Layer) |
| High maintenance effort (hardcoded logic) | Higher operational cost; regression risk | Transformation Layer (parameterize rules, dbt tests); Monitoring Components (automated checks) |
| Technical debt (no history, poor logging) | Audit/regulatory risk; slow debugging | Validation Layer (tests, audit reports); Metadata Repository; Snowflake features (clones/time travel) |
| Knowledge dependency (tribal knowledge) | Single point of failure; project delays | AI Analysis + Documentation + Human-in-the-Loop (review & capture) → Metadata Repository |

---

## Practical next steps (based on the sample)

1. Run automated extraction on sp_load_customer_orders to generate a structured spec (inputs, outputs, transformations, business-rule candidates).
2. Surface ambiguous rules (aging discount, 24‑month window, tier thresholds) as explicit review items for SMEs in the Human-in-the-Loop checkpoint.
3. Map monolithic steps to modular dbt models with associated tests and idempotent load logic; prefer INSERT/CTAS + MERGE at the dbt level rather than large procedural commits.
4. Add change/version metadata and standard logging in the transformed artifacts; capture these in the Metadata Repository for ongoing governance.

---

References

- See docs/project-outline-source.md Sections 1–3 and Objective 1 for the original challenge list and project framing.
- Prototype sample: prototype/sample_legacy/legacy_customer_orders_etl.sql (source of all quoted examples).

(End)

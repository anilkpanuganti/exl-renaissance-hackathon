# Snowflake Capabilities Study — Relevance to Legacy ETL Modernization

This note summarizes Snowflake architectural capabilities called out in Objective 2 and maps each capability to the framework layers in docs/architecture.md. It is factual and conservative — where fine-grained behavior may change across Snowflake editions or releases, a "verify against current Snowflake documentation" note is included.

---

## 1. Separation of Compute and Storage

What it is

- Snowflake separates durable storage (cloud object stores such as AWS S3 / Azure Blob / GCS) from compute (virtual warehouses). Data is stored centrally while compute clusters are provisioned independently to run queries and transformations.

Why it matters for ETL workloads

- Independent scaling of compute and storage enables cost control: keep data stored cheaply while scaling compute only when transforming or querying.
- Simplifies concurrency: multiple warehouses can operate on the same storage without data copies, useful for parallelizing migration tasks (analysis, transformation, testing).
- Reduces data movement during migration — less copying between environments.

Relevance to this framework

- Transformation Layer (3): ELT conversion and dbt model runs can scale compute separately from stored landing and staging data.
- Landing & Staging Layers (Snowflake Target Architecture §3): raw and staged data remain in central storage while transformation compute is provisioned transiently.
- Monitoring Components: cost/usage monitoring for warehouse sizing decisions.

---

## 2. Elastic Scalability (auto-scale / multi-cluster warehouses)

What it is

- Virtual warehouses can be resized, auto-suspended/resumed, and configured as multi-cluster warehouses for concurrent workloads. Auto-scaling adjusts cluster count (or size) to meet concurrency demand.

Why it matters for ETL workloads

- ETL/ELT workloads are bursty (ingestion windows, scheduled dbt runs, validation jobs). Elastic warehouses let workloads scale during peak windows and shrink afterwards.
- Multi-cluster warehouses reduce queuing under concurrency (e.g., many validation jobs or concurrent consumers hitting marts).

Relevance to this framework

- Transformation Layer (3): scale dbt/model execution and bulk transformations during Migration Planning and Code Transformation phases.
- Validation Layer (4): run parallel QA/validation jobs (business-rule verification, tests) without contention.
- Monitoring Components: supports autoscaling policies and cost/latency trade-offs captured in orchestration.

---

## 3. Secure Data Sharing (cross-account / cross-organization)

What it is

- Snowflake Secure Data Sharing provides direct, governed access to database objects (tables, views) across accounts without copying data. Shared objects are accessed by consumer accounts; data providers retain control of access and can revoke it.

Why it matters for ETL workloads

- Enables safe, auditable sharing of migrated datasets (or partial extracts) with downstream teams, analysts, or partner organizations during cutover or phased migration.
- Useful for validating parity with legacy systems by sharing test slices with stakeholders.

Relevance to this framework

- Output Layer (5): consumption-ready marts can be shared securely to stakeholders or downstream consumers as part of deployment.
- Metadata Repository & Security Layer: sharing policies and access controls live alongside lineage and governance artifacts.
- Validation Layer (4): share snapshots/clones of datasets with QA teams without extra copies.

Note: verify cross-org sharing and reader-account options against current Snowflake documentation for edition-specific behaviors.

---

## 4. Zero-copy Cloning

What it is

- Zero-copy cloning creates a point-in-time clone of databases, schemas, or tables almost instantly without duplicating underlying storage; only metadata and new writes consume space.

Why it matters for ETL workloads

- Enables rapid, low-cost creation of test and development environments that mirror production or migrated data for functional testing, transformation validation, and developer sign-off.
- Supports experiments (e.g., schema changes, dbt model refactors) without affecting source data.

Relevance to this framework

- Validation Layer (4): create clones for validation runs, regression testing, and business-rule verification.
- Human-in-the-Loop Checkpoint: developers can sign off against cloned environments safely.
- Metadata Repository: clones preserve object metadata and lineage references for reproducible tests.

---

## 5. Time Travel

What it is

- Time Travel allows querying and restoring historical data at object-level for a retention window (configurable; default/maximum depend on edition and account settings).

Why it matters for ETL workloads

- Enables precise rollback of transformation steps or accidental data changes during migration and validation.
- Facilitates auditing and forensic comparisons between pre- and post-migration states.

Relevance to this framework

- Validation Layer (4): implement rollback strategies for failed validation steps and enable side-by-side change comparisons.
- Monitoring Components & Metadata Repository: supports audit trails and historical lineage checks.

Note: retention duration and specific rollback semantics vary by Snowflake edition and account configuration — verify against current Snowflake documentation before depending on specific retention windows.

---

## 6. Data Governance Features (RBAC, masking policies, tagging)

What it is

- Role-Based Access Control (RBAC): role/privilege model for fine-grained access to objects and operations.
- Masking Policies / Dynamic Data Masking: runtime masking of sensitive columns based on role or context.
- Row Access Policies: control visibility of rows depending on predicates and caller identity.
- Object Tagging & Classification: tags on objects for classification, policy enforcement, and automated governance.
- Access History / Usage Metadata: audit logs and INFORMATION_SCHEMA / ACCOUNT_USAGE views for governance reporting.

Why it matters for ETL workloads

- Ensures least-privilege access during migration, development, and validation phases.
- Masking and row policies allow safe sharing of sample datasets for validation without exposing PII.
- Tags and usage metadata support automated governance reports and policy enforcement across migrated assets.

Relevance to this framework

- Security Layer: enforce RBAC, masking policies, row access policies, and tagging for sensitive data in Landing, Staging, and Curated layers.
- Metadata Repository: capture tags, policies, and audit information as part of governance reports in the Output Layer.
- Validation Layer (4): include governance checks (masking applied, tags present) in validation test suites.

---

## 7. Native ELT Support (vs. traditional ETL)

What it is

- Snowflake is optimized for ELT: load raw data into the platform (Landing), then perform transformations in-place (Staging → Curated → Data Marts) using SQL, dbt, Snowpark, and server-side constructs (tasks, streams). This contrasts with traditional ETL where transformations typically execute before loading.

Why it matters for ETL modernization

- Simplifies migration by moving transformation logic into the target platform (ELT), reducing external orchestration and complex data movement.
- Leverages Snowflake's scalable compute for transformations and SQL-based tooling (dbt) to maintain versioned, testable transformation pipelines.
- Supports incremental patterns (streams + tasks) and CDC-style workloads where appropriate.

Relevance to this framework

- Transformation Layer (3): primary locus of ELT conversion, dbt model generation, and Snowflake object mapping.
- Landing / Staging / Curated / Data Mart Layers (Snowflake Target Architecture §3): maps directly to ELT stages in the reference architecture.
- Validation Layer (4) & Monitoring Components: validation and freshness checks for ELT-run outputs (dbt tests, data quality checks).

Note: Snowpark, Tasks, Streams, and exact feature semantics evolve — verify specific orchestration/processing semantics against the current Snowflake documentation if planning production automation.

---

## Capability → Framework Layer Mapping (Quick Reference)

| Snowflake Capability | Primary Framework Layer(s) |
|---|---|
| Separation of Compute & Storage | Transformation Layer; Landing & Staging; Monitoring Components |
| Elastic Scalability (auto-scale / multi-cluster) | Transformation Layer; Validation Layer; Monitoring Components |
| Secure Data Sharing | Output Layer; Metadata Repository; Security Layer |
| Zero-copy Cloning | Validation Layer; Human-in-the-Loop; Metadata Repository |
| Time Travel | Validation Layer; Monitoring Components; Metadata Repository |
| Governance (RBAC, masking, tagging) | Security Layer; Metadata Repository; Validation Layer |
| Native ELT Support | Transformation Layer; Landing/Staging/Curated/Mart Layers; Validation Layer |

---

## Practical notes & caveats

- Edition and account-level settings matter. Many retention, cloning, and scaling behaviors differ by Snowflake edition (Standard/Enterprise/Business Critical/…); verify against current Snowflake documentation and the target customer's account configuration before depending on specific limits.
- Snowflake continues to evolve (Snowpark, Tasks, Streams enhancements). Confirm feature semantics (e.g., task orchestration guarantees, Snowpark language support) against the most recent docs.
- For governance-heavy migrations, include automated checks in the Validation Layer to detect misconfigured masking/row-access policies and missing tags.

---

## Recommended short-term checklist for the PoC

1. Confirm account edition and Time Travel retention settings.
2. Design warehouse sizing and auto-scale policies for dbt/validation windows.
3. Use zero-copy clones for Validation Layer test environments and include clone lifecycle cleanup in orchestration.
4. Define RBAC and masking policies early and capture them in the Metadata Repository for automated validation.
5. Prototype Secure Data Sharing for stakeholder validation workflows (verify reader-account flows if cross-org sharing is required).

---

References

- Snowflake documentation (verify features and edition-specific behaviors): https://docs.snowflake.com

(End of study)

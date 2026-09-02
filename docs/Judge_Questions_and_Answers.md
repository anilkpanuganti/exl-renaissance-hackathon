# Judge Questions & Answers

This document is intended as a quick-reference Q&A pack for judges or client-facing discussions during the Dragons Den presentation.

## 1) What problem are you solving?
We are solving the high-cost, high-risk challenge of modernizing legacy ETL pipelines and undocumented business logic into a governed Snowflake/dbt architecture. In most enterprises, the biggest bottleneck is not the syntax conversion itself — it is discovering hidden rules, dependencies, and metadata that live in tribal knowledge and legacy SQL.

## 2) Why is this important to customers?
Customers are modernizing to cloud data platforms under pressure to reduce cost, improve governance, speed up migration, and avoid reintroducing business risk. A migration that does not capture hidden rules correctly creates operational and compliance issues after go-live.

## 3) What exactly did you build in this PoC?
We built a layered AI-assisted modernization framework: it reads legacy SQL and metadata, extracts dependencies and business rules, generates Snowflake/dbt-ready transformation scaffolds, flags ambiguous rules for human review, validates outputs against source logic, and produces migration documentation and lineage artifacts.

## 4) What makes your solution different from a generic AI copilot?
Generic copilots are good at explanation, but they can also hallucinate missing logic or invent table/column references. Our framework is designed to be fact-checked: every AI-generated output is passed through validation checks, ambiguity is explicitly flagged, and a human review checkpoint is required before a migration is considered ready.

## 5) How do you avoid hallucinations?
We combine three guardrails: structured outputs, source-grounding validation, and human review. The system validates that extracted entities exist in the legacy script, checks rule coverage against the source, and routes low-confidence or ambiguous rules for review instead of assuming they are correct.

## 6) What are the key metrics or proof points?
On the representative sample run included in the project, the validation report showed: 100% entity grounding accuracy, 100% business-rule extraction coverage, and 100% ambiguity-flag recall. The report also calls out the two ambiguous rules that require human sign-off rather than silent automation.

## 7) Why is the human-in-the-loop step important?
This is a critical enterprise control. Not every business rule is explicit in SQL. Some logic is policy-based, undocumented, or embedded in business tribal knowledge. A human review checkpoint prevents the system from silently converting risky assumptions into production logic.

## 8) How does this connect to Snowflake and dbt?
Our framework maps the modernization flow into a Snowflake-aligned target architecture: landing, staging, curated/intermediate, data mart layers, plus governance metadata, monitoring, and security controls. The generated outputs are dbt-oriented, which makes them practical for modern ELT workflows and reviewable by engineering teams.

## 9) What is the architecture in plain English?
The architecture is simple: input legacy SQL and metadata → AI analysis of business rules and dependencies → transformation to dbt/Snowflake artifacts → human review → validation → generated migration documentation and plan. Each step is designed to produce reviewable evidence, not just model output.

## 10) What is the demo story you want to tell?
We tell a clear story: legacy systems hide complexity and undocumented business rules; our framework makes those rules legible, converts them into structured transformation logic, and validates the output before a migration team signs off. The value is speed plus de-risking, not blind automation.

## 11) What are the limitations of the current PoC?
This is a proof of concept, not a production benchmark. The quantitative results are based on representative sample scripts and not a broad enterprise dataset. Real deployment would require broader validation across customer-specific patterns, prompt tuning for varied SQL dialects, and environment-specific Snowflake configuration checks.

## 12) What is the product or business model angle?
The immediate value is a diagnostic/audit service: scan a customer’s legacy ETL pipeline, uncover undocumented rules and migration risks, and produce a fact-checked modernization plan before large-scale engineering begins. A longer-term SaaS version would package this into repeatable modernization accelerators for similar customer patterns.

## 13) Why should a judge believe this is credible engineering rather than a demo-only idea?
Because the PoC includes defined layers, deterministic validation metrics, generated artifacts, lineage outputs, migration planning, and documentation. It is not just a chat prompt — it is a structured workflow that produces reviewable artifacts and supports governance and human approval.

## 14) What is the biggest risk if this is not adopted?
The biggest risk is not technology failure — it is continued migration of undocumented business logic into new platforms without adequate discovery and validation. That creates silent data-quality issues, regulatory risk, and costly downstream remediation.

## 15) What is your realistic next step?
The next step is to validate the approach on a broader set of real legacy ETL assets, tune prompts and parsing across more dialects, and incorporate it into a Snowflake sandbox workflow for deeper testing. The PoC proves the design pattern and the value proposition; the next phase is operational hardening and scale.

## 16) How would you explain this in one sentence?
We built a fact-checked AI migration framework that reads legacy ETL, extracts the real business logic, scaffolds Snowflake/dbt outputs, and forces review before anything is approved.

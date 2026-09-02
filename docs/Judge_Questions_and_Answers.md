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

---

# Part B — Technical & Live-Demo Deep Dive

The questions above cover the business narrative. The ones below are the harder,
adversarial questions a technical judge is likely to ask **during or right after
the code demo**. Every answer here is grounded in code and output that exists in
this repository — where something is unproven or currently broken, the answer
says so rather than papering over it.

## 17) Your terminal says `provider: mock`. So is there actually any AI in this?
Yes, but be precise about what you are seeing. The pipeline is provider-agnostic:
`src/llm_client.py` detects `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` and routes to
that model; with neither present it falls back to a deterministic heuristic
extractor called `mock-heuristic-v1`. The demo runs the fallback so it is
reproducible offline, at zero cost, with identical output every time. The
prompting strategy for the real-model path is fully written — see
`ANALYSIS_SYSTEM_PROMPT` in `src/ai_analysis.py` and `docs/prompt-engineering.md`.
What the demo proves is that the **framework** — extraction contract, guardrails,
validation, review gate, artifact generation — works end to end. It is not a
benchmark of any particular model's extraction quality.

## 18) Then where does the AI actually add value, versus a parser?
The AI layer does the part a parser cannot: naming the *business rule* a piece of
conditional logic implements, and judging whether that rule has a stated
justification. A parser can tell you `SYSDATE - order_date > 90` exists. It
cannot tell you that is an "Order Aging Discount Exception" with no documented
rationale. The deterministic layers around it — validation, planning, lineage —
are intentionally *not* AI, because those need to be repeatable and auditable.

## 19) You claim 100% on three metrics. One hundred percent of what?
Of one script. `legacy_customer_orders_etl.sql` contains 7 tables and 8 business
rules, hand-annotated in `ground_truth_rules.json` before any run. On that
sample: 7/7 tables grounded, 8/8 rules covered, 2/2 planted ambiguous rules
flagged. That is n=1. It demonstrates the mechanism works; it is not a claim
about accuracy across an enterprise estate, and we would not present it as one.

## 20) How is "entity grounding" actually computed — and is that check robust?
`entity_grounding_accuracy()` in `src/validate.py` checks that every table name
the model claims to have found actually appears in the source SQL text. It
currently does this with a case-insensitive **substring** match, which is the
weakest form of the check: a very short table name could match inside an
unrelated word. We know this because one of our own unit tests
(`test_entity_grounding_accuracy_some_ungrounded`) currently fails on exactly
that case, and we have not fixed it yet. For this sample it does not change the
result — all 7 table names still pass a strict word-boundary match — but
tightening that check to token matching is a known, open fix.

## 21) You wrote the legacy script *and* the ground truth. Isn't that circular?
Partly, and it is a fair challenge. The sample was deliberately constructed to
contain two rules with no stated rationale, so the ambiguity test is a test we
designed ourselves to pass. What that does prove is that the guardrail fires when
it should rather than being decorative. What it does not prove is behaviour on
someone else's code. Removing that circularity requires running against a real
client's legacy asset with rules annotated by someone who is not us — which is
exactly the next step we are proposing, not something we are claiming to have
done.

## 22) Show me it failing. Does this thing ever not say PASS?
Yes, and we can show it live. Running against the multi-job workflow sample —
`python main.py --target sample_legacy/workflow_inventory_sync` — the mock
extractor scores 100% grounding but only 16.7% rule coverage and 0% ambiguity
recall, and the pipeline correctly returns `REVIEW_REQUIRED` instead of `PASS`.
The multi-job orchestration works; the mock heuristic simply is not tuned for
those scripts. The point worth making is that the validation layer caught its own
weak extraction rather than reporting success — that is the layer doing its job.

## 23) Does the generated dbt project actually run against Snowflake?
Not yet, and we will not claim it does. The generated models are syntactically
Snowflake-flavoured dbt with proper `{{ ref() }}` wiring and a
staging → intermediate → marts layout, plus `sources.yml` and `schema.yml`. They
have not been compiled by dbt or executed against a live Snowflake account.
Standing up a Snowflake sandbox and running `dbt build` on the output is the
single most valuable hardening step remaining.

## 24) The source is Oracle-flavoured. Does anything actually get translated?
Yes — open `output/dbt_models/intermediate/int_order_line_discounts.sql`. The
legacy `(SYSDATE - o.order_date) > 90` becomes
`datediff(day, order_date, current_date()) > 90`, which is Snowflake syntax. The
tier CASE and the status normalisation buckets are carried across intact. That
said, this is rule-driven translation over a known set of constructs, not a
general-purpose transpiler — broad dialect coverage is unfinished work.

## 25) The ambiguity flag is just a field in a JSON file. What actually enforces it?
It propagates into three places, which is the point. First, the generated SQL
itself carries an inline warning — `int_order_line_discounts.sql` contains
`-- AMBIGUITY FLAGGED (AI-04): 90-day / 2% aging discount has no documented
business justification`. Second, `migration_report.md` opens with a banner
stating the report has not passed human review, and marks the rule `⚠️ YES` in a
*Needs Review* column. Third, the pipeline physically stops at the checkpoint in
`main.py` and will not proceed without an explicit keystroke. The flag is not
advisory metadata; it changes what the pipeline does.

## 26) Two flagged rules is easy. What happens at two thousand?
Honestly: the current interactive loop reviews flagged rules one at a time in a
terminal, which does not scale past a few dozen. It is the right primitive but
the wrong interface. What makes it tractable is that only *ambiguous* rules
reach a human — 2 of 8 here — so the review queue is a fraction of total rules,
and `migration_plan.json` already ranks steps by dependency order and effort so
review can be sequenced rather than done in bulk. A batched, prioritised review
UI is required work, not something we have built.

## 27) What stops a reviewer from just hitting "approve" on everything?
Nothing in the current PoC, and we should be clear about that. The gate records
the decision path — approve, edit, or reject — and an edit rewrites the rule
description that downstream validation then runs against, so an edit has real
consequences. But there is no reviewer identity, no audit log, and no
second-approver requirement. Those are standard governance controls and would be
mandatory before this touched a regulated production migration.

## 28) How does it handle a real workflow — multiple jobs with dependencies?
Workflow mode reads a `manifest.json` listing jobs in order, analyses each one
separately (writing `analysis_<job_id>.json` per job), then merges tables, rules
and dependencies into an aggregate analysis that the downstream layers run
against. `migration_planner.py` then topologically orders the combined table set
so migration steps respect dependencies. That machinery is built and runs; as
noted in Q22, the mock extractor's rule coverage on that sample is the weak part,
not the orchestration.

## 29) Where do the cost and effort numbers come from?
`src/estimator.py`, and they are heuristics — the file says so itself
(*"for planning/demos only — verify with real team data"*). It multiplies counts
of tables, rules, generated files and migration steps by fixed per-unit hour
constants at a blended $80/hour. On the sample run that yields 15.25 hours,
$1,220, and a 41.9% efficiency figure against an assumed manual baseline. Those
constants are assumptions we chose, not measurements from delivery data. Treat
them as a planning scaffold whose inputs need replacing with real numbers.

## 30) Would a client let you send their legacy code to a third-party model?
That is the first objection in any regulated account, and the architecture
anticipates it in two ways. The mock provider path means the deterministic
layers — validation, planning, lineage, documentation — run with no external
call at all. And because `llm_client.py` abstracts the provider, the same
pipeline can point at a model hosted inside the client's own boundary rather than
a public API. What does not yet exist is redaction, tokenisation, or a
data-handling policy, and no client review of this has taken place.

## 31) Are you locked into one model vendor?
No. Provider selection is a runtime concern — `LLMClient` picks Anthropic,
OpenAI, or the offline heuristic based on which key is present, with no change to
the pipeline code. The prompt contract is a JSON schema, not vendor-specific
syntax. That matters commercially: model pricing and capability move fast, and
the framework's value is the guardrails around the model, not the model itself.

## 32) Is the lineage diagram parsed from the SQL, or generated by the model?
Neither directly — it is built deterministically by `src/lineage.py` from the
`dependencies` list in the analysis output, optionally enriched to column level
using `used_columns_by_table` from the metadata interpretation step. It emits
three formats: `lineage.json` for tooling, `lineage.dot` for Graphviz, and
`lineage_mermaid.md` which is embedded in the migration report and renders
directly in any Markdown viewer. Since it is derived from analysis output rather
than generated prose, it cannot invent an edge the analysis did not assert.

## 33) What is genuinely built versus designed on paper?
Built and running: the seven-layer pipeline, both entry modes (single script and
multi-job workflow), the human review gate, three validation metrics with
thresholds, dbt model generation, metadata interpretation, migration planning,
lineage artifacts, the estimator, and the migration report. Designed but not
built: the real-model path is coded but has not been exercised in our runs, the
generated dbt has not been executed against Snowflake, and there is no reviewer
audit trail. Also currently broken: one unit test fails (Q20), and the CI
workflow invokes pytest from a directory where test collection fails.

## 34) What is the one experiment that would prove or kill this?
Take a single real legacy ETL asset from an actual client estate, have someone
outside our team annotate its business rules independently, run the pipeline
against it with a real model, and compare. Two numbers decide it: what fraction
of the independently-annotated rules we recover, and — more importantly — whether
the rules we flag as ambiguous are the ones the client's own engineers agree are
undocumented. If the guardrail flags the wrong things, the core premise fails,
and we would rather find that out on one script than after selling an
engagement.

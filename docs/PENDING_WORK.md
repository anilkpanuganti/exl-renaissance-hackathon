# Pending Work, Gaps & Enhancements

This document lists everything identified in `docs/GAP_ANALYSIS.md` as
**pending, missing, or an enhancement opportunity**, organized by priority.

Each item includes a **ready-to-paste AI prompt** — designed to be handed
directly to GitHub Copilot Chat, ChatGPT, Claude, or any coding assistant
inside this repo, so you (or a teammate) can make progress on an item without
needing to re-explain context. Each prompt assumes the assistant has access
to this repository's files (or you paste the relevant file content in
alongside it).

---

## How to Use This Document

1. Pick an item below (start with **P0** items first).
2. Copy the prompt inside its ` ```prompt ` block.
3. Paste it into GitHub Copilot Chat (in VS Code, `@workspace` mode is
   recommended so it can read repo files), ChatGPT, or Claude.
4. Review the AI's output before committing — every item that touches the
   `prototype/` code should still be run (`python main.py`) and checked
   against `docs/evaluation-rubric.md` before merging.
5. Once done, update the checkbox and status in this file, and cross-reference
   the corresponding row in `docs/GAP_ANALYSIS.md`.

---

## P0 — Blocking / High-Value Gaps

### 1. [ ] Snowflake Capabilities Study (Objective 2 standalone document)

**Why it matters:** Objective 2 is explicitly one of the 5 project
objectives and currently has zero dedicated content — only referenced by
name in `docs/architecture.md`.

```prompt
You are contributing to a hackathon project repo for a "Generative
AI-Assisted Framework for Modernizing Legacy ETL and Data Warehouse Systems
to Cloud-Native Data Platforms: A Snowflake-Based Approach" (EXL Pvt. Ltd.).

Read docs/project-outline-source.md (Objective 2 and Section 5 "Snowflake
Target Architecture") and docs/architecture.md in this repo for context.

Write a new file docs/snowflake-capabilities-study.md that analyzes
Snowflake's architectural capabilities as they relate to legacy ETL
modernization, specifically:
- Separation of compute and storage (and why this matters for ETL workloads)
- Elastic scalability (auto-scale / multi-cluster warehouses)
- Secure data sharing (cross-account/cross-org)
- Zero-copy cloning (and its use in migration testing/validation)
- Time Travel (and its use in migration rollback/auditing)
- Data Governance features (RBAC, masking policies, tagging)
- Native ELT support (vs. traditional ETL)

For each capability, include a short subsection: "Relevance to this
framework" that explicitly ties it back to a layer in docs/architecture.md
(e.g., Time Travel → Validation Layer rollback strategy). Keep it factual,
concise, and structured with markdown headers and tables where useful.
Do not invent Snowflake features that don't exist — if unsure about a
specific capability's current behavior, note it as "verify against current
Snowflake documentation" rather than guessing.
```

---

### 2. [ ] Legacy ETL Challenges Analysis (Objective 1 standalone document)

**Why it matters:** Objective 1 has no dedicated analysis artifact — only
narrative background text in the original outline.

```prompt
Read docs/project-outline-source.md (Sections 1-3, and Objective 1) and
prototype/sample_legacy/legacy_customer_orders_etl.sql in this repo.

Write a new file docs/legacy-etl-challenges-analysis.md that:
1. Synthesizes the legacy ETL challenges named in the requirement document
   (complex workflow dependencies, proprietary tools, incomplete
   documentation, high maintenance effort, technical debt, knowledge
   dependency on senior developers) into a structured analysis.
2. For EACH challenge, points to a concrete example from
   prototype/sample_legacy/legacy_customer_orders_etl.sql that illustrates
   it (e.g., "Knowledge dependency" -> the undocumented 90-day aging
   discount and 24-month order window in the sample script).
3. Includes a short table: Challenge | Business Impact | How This Framework
   Addresses It (referencing the relevant layer in docs/architecture.md).

Keep the tone analytical and grounded in the actual sample code, not
generic ETL-modernization commentary.
```

---

### 3. [ ] Business Benefits Evaluation (Objective 5 standalone document)

**Why it matters:** `docs/evaluation-rubric.md` measures PoC *technical*
accuracy, but Objective 5 asks for *business* benefit evaluation
(productivity, knowledge management, governance, time-to-market).

```prompt
Read docs/evaluation-rubric.md, docs/architecture.md, and Objective 5 in
docs/project-outline-source.md.

Write a new file docs/business-benefits-evaluation.md that evaluates the
proposed framework (not just the PoC's raw output accuracy) against these
business benefit categories named in the requirement document:
- Migration productivity
- Development effort reduction
- Documentation quality
- Standardization
- Knowledge management
- Governance
- Project risk reduction
- Time-to-market

For each category, write 2-4 sentences that:
(a) explain the expected qualitative benefit,
(b) reference specific evidence from the working PoC where applicable
    (e.g., docs/evaluation-rubric.md's 100% entity grounding accuracy
    result supports the "governance" and "risk reduction" claims), and
(c) are honest about what is NOT yet proven (e.g., "productivity gains are
    estimated, not measured against a real team's manual baseline").

End with a short "Limitations of This Evaluation" section acknowledging
this is based on a single sample pipeline (n=1), consistent with the
project's stated PoC scope.
```

---

### 4. [ ] Literature Review

**Why it matters:** Methodology Phase 1 in the requirement document. Zero
content exists beyond an indicative reference list.

```prompt
Read docs/references.md and Section 6 "Proposed Methodology > Phase 1:
Literature Review" in docs/project-outline-source.md.

Write a new file docs/literature-review.md structured around these
themes (as named in the requirement document):
- Legacy ETL modernization approaches
- Cloud migration strategies
- Enterprise data warehousing (cite Kimball/Inmon concepts)
- Snowflake architecture
- Metadata-driven engineering
- Generative AI and LLMs in software engineering
- Software modernization research

For each theme, write a short (3-5 sentence) synthesis paragraph explaining
the established thinking in that area and where this project's framework
fits in / extends it. Use the sources in docs/references.md as anchors,
but be clear that this is a structured summary for a hackathon project, not
a peer-reviewed systematic literature review - don't fabricate specific
findings, page numbers, or quotes from these sources. Where you are
uncertain of a specific claim, phrase it generally (e.g., "the data
warehousing literature generally emphasizes...") rather than attributing a
specific unverifiable claim to a specific source.
```

---

## P1 — Important Enhancements

### 5. [ ] Interactive Human-in-the-Loop Checkpoint (currently simulated/auto-approved)

**Why it matters:** `main.py::human_checkpoint()` currently just prints and
auto-approves. A real review gate that can reject/edit a rule would make
the demo materially more convincing.

```prompt
Open prototype/main.py and look at the human_checkpoint() function.

Modify it so that when ambiguous rules are found (business_rules with
ambiguity_flag=true), the function actually prompts for input() from the
terminal, offering the reviewer three options per flagged rule:
  [a]pprove as-is, [e]dit the rule description, [r]eject and halt pipeline.

If the reviewer edits a description, update the in-memory analysis dict
before it's passed to the Validation Layer. If the reviewer rejects, the
pipeline should print a clear message and sys.exit(1) rather than
proceeding to Phase 4.

Keep a --auto-approve CLI flag (argparse) that preserves today's
non-interactive behavior for CI/scripted runs, since the pipeline
currently needs to run non-interactively for automated testing.

After making the change, run `python main.py` manually once to confirm
both the interactive and --auto-approve paths work, and update
prototype/README.md's "Quick Start" section to mention the new flag.
```

---

### 6. [ ] Metadata Interpretation Component (named in scope, not implemented)

**Why it matters:** "Metadata interpretation" is explicitly named as an
in-scope AI-Assisted Analysis activity and an AI Analysis Layer capability
in docs/architecture.md, but no code implements it — the PoC only reads raw
SQL text.

```prompt
Read prototype/src/ai_analysis.py and docs/architecture.md (AI Analysis
Layer description, which names "metadata interpretation" as a capability).

Create a new file prototype/sample_legacy/legacy_metadata.json containing
representative column-level metadata for the tables referenced in
prototype/sample_legacy/legacy_customer_orders_etl.sql (data types, nullable
flags, a couple of stale/misleading column comments like a legacy system
would actually have - e.g. a column comment that no longer matches what the
column is actually used for).

Then create prototype/src/metadata_interpreter.py with a function
interpret_metadata(metadata_json: dict, sql_text: str) -> dict that:
- Cross-references declared metadata against actual SQL usage
- Flags columns referenced in SQL but absent from metadata (undocumented
  columns) and columns declared in metadata but never used in the SQL
  (dead/unused columns)
- Flags any column comment that appears inconsistent with how the column
  is actually used in the SQL (e.g., a comment describing one purpose while
  the SQL clearly uses it for another)

Wire this into prototype/main.py as a new step between Phase 2 (AI
Analysis) and Phase 3 (Transformation), writing its output to
prototype/output/metadata_interpretation.json, and add its findings into
the migration report in prototype/src/generate_docs.py under a new "##
Metadata Interpretation Findings" section.

Follow the existing code style (see ai_analysis.py and validate.py for
conventions - dataclasses/dict returns, docstrings referencing
docs/architecture.md). Test by running python main.py after the change and
confirm the new output file appears and the migration report includes the
new section.
```

---

### 7. [ ] Second Sample Legacy Asset (multi-job workflow, not just one script)

**Why it matters:** Current PoC has only one sample (n=1). A second,
differently-shaped sample — ideally a multi-step **workflow** with
scheduling/orchestration dependencies, since "workflow explanation" is
explicitly named in Objective 4 — would substantially strengthen the demo
and give the evaluation metrics more than one data point.

```prompt
Read prototype/sample_legacy/legacy_customer_orders_etl.sql and
prototype/sample_legacy/ground_truth_rules.json as a reference for style
and structure.

Create a second, different representative legacy ETL asset that
demonstrates a MULTI-JOB WORKFLOW (not a single script) - for example, a
3-4 step legacy Informatica-style or shell-orchestrated batch job chain
with:
  - a job dependency/scheduling definition (e.g. a simple XML or JSON
    "workflow manifest" listing job order and dependencies, since real
    legacy orchestration tools like Informatica/AutoSys/Control-M produce
    this kind of artifact)
  - 2-3 SQL/stored-procedure scripts that the workflow calls in sequence
  - at least one embedded, realistically undocumented business rule,
    matching the style already used in the customer orders sample

Save these under prototype/sample_legacy/workflow_inventory_sync/ (create
the folder) with a manifest file, the SQL scripts, and a
ground_truth_rules.json following the same schema as the existing one.

Do NOT wire this into main.py yet - just create the sample assets and a
short prototype/sample_legacy/workflow_inventory_sync/README.md explaining
the scenario. Wiring it into the pipeline is a separate follow-up task
(see item #8 below).
```

---

### 8. [ ] Extend Pipeline to Support Multiple Samples / Workflow-Level Analysis

**Why it matters:** Follow-up to item #7 — once a multi-job sample exists,
`main.py` needs to support analyzing a workflow (multiple related files),
not just a single SQL file.

```prompt
This depends on item #7 being done first (a multi-job sample under
prototype/sample_legacy/workflow_inventory_sync/ must exist).

Read prototype/main.py, prototype/src/ai_analysis.py, and the new workflow
sample folder.

Refactor prototype/main.py so it can run against EITHER:
 (a) a single SQL file (today's behavior, default), or
 (b) a workflow folder containing a manifest + multiple SQL files

Add a --target argument (argparse) accepting a file path or folder path.
When given a folder, read the manifest to determine job order, run the
existing analyze_legacy_sql() against each job's SQL in sequence, and
merge results into a single analysis dict with an added "workflow_jobs"
list preserving per-job breakdowns alongside the aggregate.

Update prototype/src/generate_docs.py so the migration report includes a
per-job breakdown section when workflow_jobs is present, in addition to the
existing aggregate view.

Keep the existing single-file default behavior 100% backward compatible -
running `python main.py` with no arguments must still work exactly as it
does today. Test both paths after the change.
```

---

### 9. [ ] Migration Planning Artifact Generator

**Why it matters:** "Migration planning" is explicitly named in Objective 4
as something the PoC should demonstrate, but no component currently
produces a plan/timeline/sequencing output.

```prompt
Read prototype/src/generate_docs.py and docs/architecture.md (Modernization
Workflow: Discovery -> Assessment -> AI Analysis -> Migration Planning ->
Transformation -> Human Review -> Validation -> Documentation ->
Deployment).

Create prototype/src/migration_planner.py with a function
generate_migration_plan(analysis: dict, validation: dict) -> dict that
produces a simple, deterministic migration plan given the AI Analysis and
Validation outputs already available in the pipeline:
  - Sequences migration steps based on table dependencies already present
    in analysis["dependencies"] (dimension tables before fact tables, etc.)
  - Assigns a rough relative-effort tag (Low/Medium/High) per table based
    on how many business rules touch it and whether any are ambiguity-flagged
  - Flags any table/rule that failed validation (from the validation dict)
    as a "blocking item" that must be resolved before that step proceeds

Wire this in as a new step in prototype/main.py after Phase 4 (Validation)
and before Phase 5 (Documentation), writing output to
prototype/output/migration_plan.json, and add a "## Migration Plan"
section to the report generated in generate_docs.py showing the sequenced
steps as a simple ordered table.

This should remain a deterministic/rule-based component (not an LLM call)
since it's sequencing already-known data, not generating new interpretation
- follow the pattern of validate.py rather than ai_analysis.py.
```

---

## P2 — Nice-to-Have / Polish

### 10. [ ] Validate Pipeline Against a Real LLM (Anthropic or OpenAI)

**Why it matters:** The pipeline has only ever been run in mock mode.
Real-LLM behavior/accuracy is unverified.

```prompt
Read prototype/src/llm_client.py and prototype/README.md.

I have an ANTHROPIC_API_KEY (or OPENAI_API_KEY) available in my
environment. Walk me through:
1. Installing the right SDK (pip install anthropic, or openai)
2. Setting the environment variable correctly for my OS
3. Running python main.py from the prototype/ folder
4. What to check in the output (prototype/output/analysis.json,
   validation_report.json) to confirm the real LLM produced sensibly
   different results from mock mode - specifically, compare whether the
   real LLM correctly flagged the same two ambiguous rules (AI-04 aging
   discount, AI-07 24-month window) that the mock heuristic catches by
   design.

If the real LLM's JSON output doesn't match the expected schema exactly,
help me debug prototype/src/ai_analysis.py's JSON-parsing fallback logic
to handle it, without changing the strict prompt rules already defined in
ANALYSIS_SYSTEM_PROMPT.
```

---

### 11. [ ] Unit Tests for Prototype Modules

**Why it matters:** Zero automated tests currently exist for `ai_analysis.py`,
`transform.py`, `validate.py`, `generate_docs.py`.

```prompt
Read all files in prototype/src/ and prototype/main.py.

Create a prototype/tests/ folder with pytest-style unit tests:
- test_validate.py: test entity_grounding_accuracy(), business_rule_coverage(),
  and ambiguity_flag_recall() using small hand-built analysis/ground_truth
  dicts (don't require an LLM call - these are pure functions)
- test_transform.py: test generate_dbt_models() writes all expected files
  given a minimal analysis dict, using a tmp_path fixture for output_dir
- test_generate_docs.py: test generate_migration_report() produces expected
  section headers given minimal analysis/validation inputs

Do NOT write a test that calls a real LLM API. For llm_client.py's mock
mode, you may write one test confirming _mock_analysis() returns valid JSON
with the expected keys (tables, business_rules, dependencies) given the
existing sample SQL file.

Add pytest to prototype/requirements.txt as a dev dependency (comment it
as such) and add a "Running Tests" section to prototype/README.md with the
command to run them (cd prototype && pytest tests/ -v).
```

---

### 12. [ ] GitHub Actions CI Workflow

**Why it matters:** No CI currently runs the pipeline or tests on push/PR.

```prompt
Create .github/workflows/ci.yml that, on every push and pull_request to
any branch:
1. Sets up Python 3.11
2. Installs prototype/requirements.txt (mock mode needs no extra deps, but
   install anyway for future-proofing)
3. Runs `cd prototype && python main.py` and fails the build if it exits
   non-zero
4. If prototype/tests/ exists (see item #11), also runs `pytest tests/ -v`

Keep it simple - no matrix builds, no deployment steps, since this is a
hackathon PoC repo, not a production service. Add a small badge to the top
of the root README.md linking to the workflow status.
```

---

### 13. [ ] Consolidated Project Report (final deliverable)

**Why it matters:** Explicitly listed as a deliverable in Section 5 of the
requirement document; nothing currently consolidates the framework design +
PoC results + evaluation into one narrative report.

```prompt
This task should be done LAST, after items #1-4 (Snowflake study, legacy
challenges analysis, business benefits evaluation, literature review) exist
as files under docs/.

Read every file under docs/ in this repo (project-outline-source.md,
architecture.md, prompt-engineering.md, evaluation-rubric.md,
competitive-landscape.md, and the newly created
snowflake-capabilities-study.md, legacy-etl-challenges-analysis.md,
business-benefits-evaluation.md, literature-review.md) plus
prototype/output/migration_report.md from a real pipeline run.

Write docs/PROJECT_REPORT.md as a consolidated report following the
original Table of Contents in docs/project-outline-source.md (Background,
Problem Statement, Motivation, Objectives, Scope, Methodology, Plan of
Work, Resources, Risks, Expected Benefits, References, Glossary), but
updated to reflect what was ACTUALLY BUILT and FOUND, not just what was
proposed. Each section should reference the specific supporting document
or PoC result rather than repeating the original proposal text verbatim.
Keep the tone appropriate for a hackathon project report submission.
```

---

### 14. [ ] Presentation Deck

**Why it matters:** Explicitly listed as a deliverable; nothing exists yet.

```prompt
Read docs/PROJECT_REPORT.md (or, if not yet created, docs/architecture.md
and docs/evaluation-rubric.md plus a real run's
prototype/output/migration_report.md) in this repo.

Create a slide-by-slide outline (as a markdown file,
docs/presentation-outline.md) for a 10-12 slide hackathon presentation
covering: Problem, Motivation, Framework Overview (with the layered
diagram), Live PoC Demo walkthrough (what the audience will see run),
Validation Results (the actual metrics achieved), Business Benefits,
Limitations & Future Work, Q&A. For each slide, give a suggested title and
3-5 bullet points of content pulled from the actual repo content (not
generic placeholders).
```

---

## Tracking

| # | Item | Priority | Status |
|---|---|---|---|
| 1 | Snowflake Capabilities Study | P0 | ⬜ Not started |
| 2 | Legacy ETL Challenges Analysis | P0 | ⬜ Not started |
| 3 | Business Benefits Evaluation | P0 | ⬜ Not started |
| 4 | Literature Review | P0 | ⬜ Not started |
| 5 | Interactive Human-in-the-Loop Checkpoint | P1 | ⬜ Not started |
| 6 | Metadata Interpretation Component | P1 | ⬜ Not started |
| 7 | Second Sample (Multi-Job Workflow) | P1 | ⬜ Not started |
| 8 | Extend Pipeline for Workflow-Level Analysis | P1 | ⬜ Not started (depends on #7) |
| 9 | Migration Planning Artifact Generator | P1 | ⬜ Not started |
| 10 | Validate Against Real LLM | P2 | ⬜ Not started |
| 11 | Unit Tests | P2 | ⬜ Not started |
| 12 | GitHub Actions CI | P2 | ⬜ Not started |
| 13 | Consolidated Project Report | P2 | ⬜ Not started (do last) |
| 14 | Presentation Deck | P2 | ⬜ Not started (do last) |

Update the Status column as items are completed (⬜ Not started → 🟨 In
progress → ✅ Done), and add a short note (date, who/what closed it) next to
each row as you go.

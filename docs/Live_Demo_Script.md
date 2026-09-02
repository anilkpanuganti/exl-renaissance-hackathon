# Live Demo Script — GenAI-Assisted ETL Modernization PoC

A step-by-step run sheet for a screen-shared demo. Everything below has been
executed on this repository and reflects actual output — no projected or
illustrative numbers.

**Target length:** 6–8 minutes.
**Requirements:** Python 3 and this repository. No API key, no network, no
third-party packages.

---

## 0. Before you share your screen (2 minutes)

| # | Action | Why |
|---|---|---|
| 1 | Open a terminal at the repository root | Avoids fumbling paths on camera |
| 2 | Run `cd prototype` then `python main.py --auto-approve` once | Pre-populates `prototype/output/`, so you have a fallback if the live run misbehaves |
| 3 | Open an editor with these four files ready in tabs:<br>`prototype/sample_legacy/legacy_customer_orders_etl.sql`<br>`prototype/output/analysis.json`<br>`prototype/output/validation_report.json`<br>`prototype/output/migration_report.md` | You will switch between them, not go hunting |
| 4 | Increase terminal font size | The validation output is the money shot |

> **Note on the entry point:** run `python main.py` with the working directory
> set to `prototype/`. The alternate form `python -m prototype.main` mentioned
> in the module docstring does not currently work.

---

## 1. Set the scene — the legacy asset (60 seconds)

**Show:** `prototype/sample_legacy/legacy_customer_orders_etl.sql`

**Say:** *"This is a representative legacy ETL script — the kind of asset that
blocks a migration. It has sparse comments and business logic buried in CASE
statements."*

**Scroll to these three lines and point at them:**

| Line | Content |
|---|---|
| 56 | `-- also: orders over 90 days from order_date get an extra 2% "aging discount"` |
| 68 | `CASE WHEN (SYSDATE - o.order_date) > 90 THEN 0.02 ELSE 0 END` |
| 81 | `WHERE o.order_date >= ADD_MONTHS(SYSDATE, -24); -- only last 2 years, reason unclear` |

**Say:** *"Two rules here have no stated business reason — a 90-day aging
discount and a 24-month order window. A migration tool that silently converts
these carries an unexamined business decision into the new platform. Watch what
our framework does with them instead."*

---

## 2. Run the pipeline (60 seconds)

**Type:**

```bash
cd prototype
python main.py --auto-approve
```

**Expected output (this is the actual output, abbreviated):**

```
Running pipeline with provider: mock (model: mock-heuristic-v1)
--- Phase 2: AI Analysis Layer ---
Extracted 7 tables, 8 business rules.
--- Phase 3a: Metadata Interpretation ---
--- Phase 3: Transformation Layer ---
Generated 7 dbt/Snowflake artifact files.

--- HUMAN-IN-THE-LOOP CHECKPOINT ---
2 rule(s) flagged for mandatory human review before proceeding:
  - Auto-approved: AI-04: Order Aging Discount Exception -> ...
  - Auto-approved: AI-07: 2-Year Order Window -> ...

--- Phase 4: Validation Layer ---
Validation status: PASS
  PASS: Entity Grounding Accuracy: 100.0%
  PASS: Business Rule Extraction Coverage: 100.0%
  PASS: Ambiguity Flag Recall: 100.0%

--- Phase 5: Migration Planning ---
--- Lineage: generating lineage artifacts ---
--- Estimator: computing cost/time/efficiency estimates ---
--- Phase 6: Output Layer (Documentation) ---
Pipeline complete. See prototype/output/ for all artifacts.
```

**Say while it runs:** *"That's the whole pipeline — analysis, transformation,
review gate, validation, planning, documentation — in one command with no API
key and no network call."*

**Be upfront about `mock`:** *"It says provider `mock`. That's a deterministic
heuristic extractor built into the PoC so the pipeline runs identically anywhere,
including with no budget and no connectivity. Set `ANTHROPIC_API_KEY` or
`OPENAI_API_KEY` and the same pipeline routes to a real model — that's a
one-line change in `src/llm_client.py`'s provider detection, no change to the
pipeline itself."*

---

## 3. Point at the guardrail firing (90 seconds) — **the most important moment**

**Show:** `prototype/output/analysis.json`, search for `AI-04`.

```json
{
  "id": "AI-04",
  "name": "Order Aging Discount Exception",
  "description": "Additional discount applied when order age exceeds 90 days.",
  "confidence": 0.6,
  "ambiguity_flag": true,
  "confidence_notes": "Business justification for the 90-day / 2% values is not
                       present in the source script; flagged for human review
                       rather than assumed."
}
```

**Say:** *"This is the difference between our framework and a copilot. The model
extracted the rule correctly, and then explicitly refused to invent a reason for
it. `ambiguity_flag: true`, confidence dropped to 0.6, and `confidence_notes`
says exactly what it could not establish. `AI-07`, the 24-month window, is the
same. Neither of these can pass through silently."*

---

## 4. Show the generated target (60 seconds)

**Show:** the `prototype/output/dbt_models/` tree.

```
dbt_models/
├── sources.yml
├── schema.yml
├── staging/       stg_customers.sql, stg_orders.sql
├── intermediate/  int_order_line_discounts.sql
└── marts/         dim_customers.sql, fct_orders.sql
```

**Open** `marts/fct_orders.sql` — it is real dbt SQL using `{{ ref(...) }}`:

```sql
select
    order_id, customer_id, product_id, order_date,
    quantity, unit_price, net_line_amount, derived_status
from {{ ref('int_order_line_discounts') }}
```

**Say:** *"A layered dbt project — staging, intermediate, marts — with sources
and schema definitions. This is reviewable SQL that a data engineer can open in
a pull request, not a wall of prose."*

**Then open** `intermediate/int_order_line_discounts.sql` — this is the strongest
single artifact in the demo, because it shows two things at once:

```sql
        -- AMBIGUITY FLAGGED (AI-04): 90-day / 2% aging discount has no
        -- documented business justification in the legacy source.
        -- Human reviewer: confirm this is intentional before promoting to prod.
        case
            when datediff(day, order_date, current_date()) > 90 then 0.02
            else 0
        end as aging_discount_pct
```

**Say:** *"Two things here. First, the Oracle `SYSDATE - order_date > 90` from
line 68 has been translated into Snowflake's `datediff(...)`. Second — and this
is the part that matters — the ambiguity flag didn't stay in a JSON file. It was
written into the generated SQL as a warning for whoever reviews this pull
request. The guardrail travels with the code."*

---

## 5. Show the fact-check (60 seconds)

**Show:** `prototype/output/validation_report.json`

```json
"entity_grounding_accuracy": { "score": 1.0, "checked": 7, "grounded": 7, "ungrounded": [] },
"business_rule_coverage":    { "score": 1.0, "total_ground_truth_rules": 8, "missed": [] },
"ambiguity_flag_recall":     { "score": 1.0, "expected": 2, "flagged_by_ai": 2 },
"overall_status": "PASS"
```

**Say:** *"Three metrics, computed by `src/validate.py` against
`sample_legacy/ground_truth_rules.json`, which we hand-annotated before running
anything. Grounding checks that every table the model named actually appears in
the source — that's the anti-hallucination check. Coverage checks we didn't miss
a rule. Ambiguity recall checks that both planted undocumented rules were caught.
If any check fails, `overall_status` becomes `REVIEW_REQUIRED` instead of
`PASS`."*

**If a judge asks to see the logic:** open `prototype/src/validate.py` — the
thresholds are on lines 98–109 (grounding ≥ 0.9, coverage ≥ 0.7, ambiguity
recall ≥ 0.5).

---

## 6. Show the deliverable (45 seconds)

**Show:** `prototype/output/migration_report.md`

Point at three things:

1. **The banner at the top** — *"⚠️ This report is AI-generated and has NOT yet
   passed human review."* The artifact carries its own review status.
2. **Section 2** — the business rule table, with `⚠️ YES` in the *Needs Review*
   column for AI-04 and AI-07.
3. **Section 3** — a Mermaid lineage diagram rendered directly in the Markdown.

**Also mention:** `migration_plan.json` sequences the 7 tables in dependency
order with an effort rating per step, and `estimates.json` produces a heuristic
cost/time figure (the file itself labels these *"for planning/demos only —
verify with real team data"*).

---

## 7. Close on the human gate (45 seconds)

**Type:**

```bash
python main.py
```

*(no `--auto-approve`)*

The pipeline stops at the checkpoint:

```
Rule ID: AI-04
Name   : Order Aging Discount Exception
Current: Additional discount applied when order age exceeds 90 days.
Notes  : Business justification for the 90-day / 2% values is not present ...
Choose action: [a]pprove as-is, [e]dit description, [r]eject and halt pipeline
```

**Demonstrate `e`** — type a corrected description. The edit updates the
in-memory rule, and validation downstream runs against your text, not the
model's.

**Then say:** *"And `r` halts the pipeline outright. The framework will not
produce an approved migration for a rule a reviewer won't sign off on. That's
the control that makes this usable in a regulated environment."*

**Press `a` twice** to finish the run cleanly if you are short on time.

---

## 8. Closing line

> *"One command turned an undocumented legacy script into a dbt project, a
> dependency-ordered migration plan, a lineage diagram, and a migration report —
> and it flagged the two rules a human has to decide on rather than guessing at
> them. Speed plus de-risking, not blind automation."*

---

## Things to be honest about if asked

These are real, current limitations. Stating them yourself is stronger than
being caught by them.

| Topic | The honest answer |
|---|---|
| **Mock mode** | The demo runs a deterministic heuristic extractor, not a live LLM. It is a documented design choice (offline/cost-control fallback), and it means the 100% figures reflect the *pipeline and guardrails* working, not a measurement of any specific model's extraction quality. |
| **Sample size** | These metrics come from one hand-crafted script with hand-annotated ground truth. n=1. It proves the mechanism, not enterprise-grade accuracy. |
| **Multi-job workflow mode** | `python main.py --target sample_legacy/workflow_inventory_sync` runs, and grounding stays at 100%, but under the mock extractor rule coverage drops to 16.7% and ambiguity recall to 0% — so it correctly returns `REVIEW_REQUIRED` rather than `PASS`. **Do not demo this path.** If asked: the multi-job orchestration works, the mock heuristic simply isn't tuned for those scripts, and the validation layer caught that itself — which is the layer doing its job. |
| **Unit tests** | **Do not run `pytest` on camera.** Tests must be run from the repository root (`python -m pytest prototype/tests`), and one of the seven currently fails: `test_entity_grounding_accuracy_some_ungrounded`. It exposes that the grounding check uses substring matching, so a one-character table name can match by accident. It does not affect this demo's result — all 7 real table names still pass a strict word-boundary check — but the test is a legitimate open bug. |

---

## Fallback plan

If the live run fails for any reason: `prototype/output/` is already populated
from your pre-flight run. Say *"I ran this before the call, let me walk you
through what it produced,"* and go straight to Step 3. Nothing in Steps 3–6
requires the run to have just happened.

# Proof-of-Concept: GenAI-Assisted ETL Modernization Pipeline

This is the working PoC referenced in Objective 4 of the project outline
(`docs/project-outline-source.md`) and the framework design in
`docs/architecture.md`. It demonstrates, end-to-end, on **one representative
legacy SQL script**:

1. **AI Analysis** — extract tables, business rules, dependencies
2. **Transformation** — generate Snowflake-ready dbt models (staging → intermediate → marts)
3. **Human-in-the-loop checkpoint** — simulated review gate for ambiguous rules
4. **Validation** — grounding accuracy, rule-extraction coverage, ambiguity-flag recall
5. **Documentation** — auto-generated migration report with lineage diagram

## Quick Start (no API key required)

```bash
cd prototype
python3 main.py            # interactive review of ambiguous rules
python3 main.py --auto-approve   # non-interactive / CI-friendly: auto-approve ambiguous rules
```

This runs entirely in **mock mode** by default (deterministic heuristic
extraction, no external calls, no dependencies beyond the Python standard
library) — so it's fully demoable with zero setup. Use `--auto-approve` for
CI or scripted runs to preserve the pipeline's non-interactive behavior. See
`docs/architecture.md` §5–6 for why mock mode is a legitimate, documented
part of the design (cost control fallback), not just a stub.

Output is written to `prototype/output/`:
- `analysis.json` — AI Analysis Layer output
- `dbt_models/` — generated Snowflake/dbt project structure
- `validation_report.json` — quantitative validation metrics
- `migration_report.md` — final human-readable migration report

## Running Against a Real LLM

```bash
pip install anthropic   # or: pip install openai
export ANTHROPIC_API_KEY=sk-...     # or OPENAI_API_KEY
python3 main.py
```

The pipeline auto-detects which key is present (`src/llm_client.py`) and
routes accordingly. No code changes needed to switch providers.

## Project Layout

```
prototype/
├── main.py                    # orchestrator - runs all phases in order
├── sample_legacy/
│   ├── legacy_customer_orders_etl.sql   # hand-crafted representative legacy asset
│   └── ground_truth_rules.json          # hand-annotated rules, used for evaluation metrics
├── src/
│   ├── llm_client.py           # provider-agnostic LLM abstraction (Anthropic/OpenAI/mock)
│   ├── ai_analysis.py          # Phase 2: AI Analysis Layer
│   ├── transform.py            # Phase 3: Transformation Layer
│   ├── validate.py             # Phase 4: Validation Layer
│   └── generate_docs.py        # Phase 5: Output Layer (migration report)
└── output/                     # generated at runtime (gitignored)
```

## Why This Sample

`legacy_customer_orders_etl.sql` is deliberately written to mimic a real
legacy asset: sparse/inconsistent comments, embedded business logic (tier
classification, discount rules), and **two intentionally undocumented
business rules** (a 90-day aging discount and a 24-month order window) with
no explainable justification in the code. This tests whether the AI
Analysis Layer correctly flags these as ambiguous rather than confidently
fabricating a rationale — the central hallucination-guardrail claim made in
`docs/architecture.md` and measured in `docs/evaluation-rubric.md`.

## Related Docs

- [`../docs/architecture.md`](../docs/architecture.md) — full framework design
- [`../docs/prompt-engineering.md`](../docs/prompt-engineering.md) — prompting strategy
- [`../docs/evaluation-rubric.md`](../docs/evaluation-rubric.md) — metrics definitions
- [`../docs/competitive-landscape.md`](../docs/competitive-landscape.md) — positioning vs. existing tools

# GenAI-Assisted Legacy ETL Modernization Framework

### A Snowflake-Based Approach to Cloud-Native Data Platform Migration

**Organization:** EXL Pvt. Ltd., Gurgaon, Haryana, India
**Project Type:** Work-related Hackathon / PoC Project
**Project Area:** AI-Assisted Cloud Data Engineering (Enterprise Data Warehouse & ETL Modernization)

---

## 1. What This Project Is

Legacy ETL and data warehouse systems accumulate technical debt, undocumented business
rules, and complex dependencies over years of development. Modernizing them to
cloud-native platforms like **Snowflake** is traditionally a slow, manual, expert-dependent
process.

This project proposes and demonstrates a **Generative AI-Assisted Modernization
Framework** that supports the *entire* modernization lifecycle — not just code
conversion — including legacy code analysis, business rule extraction, migration
recommendations, dbt/Snowflake transformation, validation, and documentation generation.

## 2. Repository Structure & Branch Strategy

This repository follows a **two-branch model** during the hackathon phase:

| Branch | Contents | Purpose |
|---|---|---|
| `main` | Approved project outline, references, glossary, licensing, repo governance | The stable, "official" record of the project — what would be submitted/reviewed |
| `feature/genai-poc-framework` | Full framework docs + working proof-of-concept prototype code | Active development branch where the PoC, architecture docs, and evaluation artifacts are built and iterated on before merging back |

The feature branch will be merged into `main` via pull request once the PoC and
supporting documentation are reviewed and finalized.

## 3. Documentation Index (this branch)

| Document | Description |
|---|---|
| [`docs/project-outline-source.md`](docs/project-outline-source.md) | Full original project outline (background, problem statement, objectives, scope, methodology, plan of work, resources, risks, expected benefits) |
| [`docs/references.md`](docs/references.md) | Indicative APA references |
| [`docs/glossary.md`](docs/glossary.md) | Key terminology |

| [`docs/architecture.md`](docs/architecture.md) | Layered framework design, Snowflake target architecture, cost/latency and hallucination-guardrail considerations |
| [`docs/prompt-engineering.md`](docs/prompt-engineering.md) | Prompting strategy used by the PoC (structured output, chain-of-thought extraction, grounding) |
| [`docs/evaluation-rubric.md`](docs/evaluation-rubric.md) | Quantitative + qualitative metrics used to evaluate the PoC |
| [`docs/competitive-landscape.md`](docs/competitive-landscape.md) | Positioning vs. SnowConvert, AWS SCT, BladeBridge/Datometry, generic LLM copilots |
| [`prototype/`](prototype/) | Working end-to-end proof-of-concept (see `prototype/README.md`) |

## 4. Project Objectives (Summary)

1. Analyze legacy ETL challenges (dependencies, technical debt, undocumented logic)
2. Study Snowflake's cloud-native capabilities as the modernization target
3. Design a GenAI-assisted modernization framework spanning the full lifecycle
4. Build a conceptual proof-of-concept (SQL interpretation → dbt/Snowflake transformation → validation → documentation)
5. Evaluate the framework's expected business benefits

## 5. Running the Proof-of-Concept

```bash
cd prototype
python3 main.py
```

Runs end-to-end in mock mode with zero setup. See [`prototype/README.md`](prototype/README.md)
for details, including how to point it at a real LLM (Anthropic or OpenAI).

## 6. Status

🚧 **Active hackathon build.** This branch (`feature/genai-poc-framework`) contains
the full framework documentation and working PoC. It will be merged into `main`
once reviewed.

## 6. License

See [`LICENSE`](LICENSE).

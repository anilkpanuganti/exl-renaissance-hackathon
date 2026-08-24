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

> Architecture diagrams, the working PoC, evaluation rubric, prompt-engineering
> approach, and competitive landscape analysis live on
> **[`feature/genai-poc-framework`](../../tree/feature/genai-poc-framework)**
> until they're reviewed and merged.

## 4. Project Objectives (Summary)

1. Analyze legacy ETL challenges (dependencies, technical debt, undocumented logic)
2. Study Snowflake's cloud-native capabilities as the modernization target
3. Design a GenAI-assisted modernization framework spanning the full lifecycle
4. Build a conceptual proof-of-concept (SQL interpretation → dbt/Snowflake transformation → validation → documentation)
5. Evaluate the framework's expected business benefits

## 5. Status

🚧 **Active hackathon build** — see the feature branch for current progress on the
proof-of-concept and supporting technical documentation.

## 6. License

See [`LICENSE`](LICENSE).

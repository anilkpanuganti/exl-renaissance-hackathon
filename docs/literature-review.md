# Literature Review — Structured Summary for the PoC

This is a concise, hackathon‑scope literature synthesis organized around the themes listed in the project's methodology. Sources in docs/references.md (Kimball, Inmon, Snowflake docs, dbt, AI and SE literature) are used as anchors; this is a structured summary for the PoC, not a systematic literature review.

---

## Legacy ETL modernization approaches

The literature and practitioner guides generally emphasize incremental, risk‑aware migration patterns: discover and catalogue legacy assets, isolate business rules, and migrate in phases rather than a big‑bang cutover. Many approaches recommend converting procedural ETL to declarative ELT patterns and introducing automated tests and lineage before cutover. This project fits by automating discovery and business‑rule extraction as early‑phase artifacts that enable phased, testable migration plans.

## Cloud migration strategies

Cloud migration work commonly stresses lift‑and‑shift for quick wins, followed by re‑architecture to exploit cloud primitives (elastic compute, managed storage, service abstractions). Migration strategy selection is driven by risk, cost, and business continuity requirements; hybrid and phased approaches are frequent in enterprise settings. The framework positions AI‑assisted discovery and modular dbt conversion to support phased migration and de-risk the re‑architecture step.

## Enterprise data warehousing (Kimball / Inmon concepts)

Classic data warehousing literature (Kimball’s dimensional modeling and Inmon’s enterprise data warehouse perspectives) emphasizes conformed dimensions, clear layer separation, and consistent grain definitions to support analytics. These foundational principles guide the target architecture (landing → staging → curated → marts) used in this project, where dbt models and metadata capture the conformance and lineage expectations advocated by those schools of thought.

## Snowflake architecture

Snowflake’s separation of storage and compute, elastic warehouses, and features like zero‑copy cloning and Time Travel are frequently cited as enablers of scalable ELT and safe testing. The platform’s managed services and sharing capabilities change operational tradeoffs compared to on‑premise RDBMS systems. The framework leverages these Snowflake capabilities to enable non‑destructive validation, scalable transformation, and secure stakeholder validation flows, while noting edition‑specific constraints should be verified in practice.

## Metadata‑driven engineering

Contemporary engineering practice emphasizes metadata as a first‑class asset: automated lineage, schema and rule catalogs, and test metadata enable repeatable, auditable pipelines. Tools like dbt and metadata stores promote treating transformations as code plus metadata for governance and reproducibility. The project extends this thinking by using AI to extract metadata from legacy artifacts and populate a Metadata Repository that drives transformation generation and validation.

## Generative AI and LLMs in software engineering

Recent research and industry experiments show LLMs can assist code comprehension, summarization, and scaffold generation, but they require guardrails to avoid hallucinations and must be integrated with verification steps. Best practice is to combine model outputs with schema/grounding checks, structured JSON outputs, and human review. The framework follows this pattern: LLMs are used for extraction and recommendation, followed by rule‑based validation and a Human‑in‑the‑Loop checkpoint to maintain correctness.

## Software modernization research

The software modernization literature highlights the importance of artifact discovery, semantic mapping, and preserving business intent during automated transformations; empirical work often stresses human oversight and staged validation. Automated translation tools can accelerate work but typically do not eliminate expert review, particularly where business rules are ambiguous. This project contributes a practical integration of AI‑assisted extraction, metadata capture, and dbt‑oriented transformation that aligns with modernization research while emphasizing explicit validation and governance.

---

## Notes on scope

This synthesis prioritizes breadth and practical relevance for the PoC. It is intentionally concise and not a substitute for a formal, peer‑reviewed literature review; sources listed in docs/references.md should be consulted for full background and citation details.

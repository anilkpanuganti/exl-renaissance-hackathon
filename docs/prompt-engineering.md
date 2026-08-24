# Prompt Engineering Strategy

The framework's credibility depends on *how* the LLM is instructed, not just
which model is used. This document describes the prompting approach used in
the PoC (`prototype/src/`).

## 1. Structured Output, Not Free Text

Every LLM call in the AI Analysis and Transformation layers requests a
**JSON object matching a fixed schema** (tables, columns, business_rules,
dependencies, confidence_notes). Free-text explanations are generated
*separately*, after the structured extraction, so machine validation never
has to parse prose.

## 2. Chain-of-Thought Extraction, Hidden from Final Output

The extraction prompt asks the model to reason step-by-step internally
(identify tables → identify joins → identify conditional logic → name the
business rule each conditional implements) before emitting the final JSON.
This measurably improves rule-extraction accuracy over asking for the JSON
directly, at the cost of a few extra output tokens.

## 3. Few-Shot Anchoring

The prompt includes one worked example: a short legacy SQL snippet paired
with its correct structured extraction. This anchors the model's definition
of what counts as a "business rule" (e.g., a discount tier threshold) versus
plain technical logic (e.g., a type cast), which is otherwise ambiguous.

## 4. Grounding Against Hallucination

The prompt explicitly instructs the model: *"Only reference tables, columns,
and values that literally appear in the provided script. If something is
ambiguous, say so in `confidence_notes` rather than guessing."* The
downstream validator (`validate.py`) then cross-checks every referenced
table/column against the actual source text — any invented entity fails
validation and is flagged for human review rather than silently passed
through.

## 5. Separation of Concerns Across Prompts

Rather than one mega-prompt doing analysis + transformation + documentation,
the framework uses **three distinct prompts**, each with a narrow
responsibility:

1. `ANALYSIS_PROMPT` — extraction only
2. `TRANSFORM_PROMPT` — Snowflake SQL + dbt generation, given the extraction as input
3. `DOC_PROMPT` — human-readable migration report, given both prior outputs as input

This keeps each call's context small and focused, makes failures easier to
localize, and allows swapping a cheaper model into any one stage
independently.

## 6. Model/Provider Abstraction

`prototype/src/llm_client.py` abstracts the provider (Anthropic, OpenAI, or
a deterministic **mock mode**) behind one interface, so the framework isn't
tied to a single vendor — consistent with the report's stated risk
mitigation ("base the framework on established AI concepts rather than
specific tool versions").

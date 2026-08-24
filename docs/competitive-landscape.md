# Competitive & Landscape Positioning

To strengthen credibility, the framework is positioned relative to existing
commercial and open approaches to ETL/DW modernization.

| Tool / Approach | Focus | Gap this framework addresses |
|---|---|---|
| **Snowflake SnowConvert** | Automated SQL dialect conversion (e.g., Teradata/Oracle → Snowflake) | Strong at syntax conversion, limited at explaining *why* a business rule exists or generating human-readable migration documentation |
| **AWS Schema Conversion Tool (SCT)** | Schema and code conversion for AWS-target migrations | Similar syntax-focused conversion; not GenAI-native, not oriented at dbt-based modern transformation patterns |
| **BladeBridge / Datometry** | Automated legacy-to-cloud code transpilation | Positioned as "lift and transpile," with less emphasis on structured documentation generation and governance reporting as first-class outputs |
| **ChatGPT / generic LLM copilots** | Ad hoc code explanation and generation | Not integrated into a structured, validated, multi-layer lifecycle; no built-in grounding/validation step against source artifacts |

## Where This Framework Differs

1. **Documentation-first, not code-first.** Business rule extraction and
   migration documentation are treated as primary deliverables, not a
   byproduct of code conversion.
2. **Explicit validation layer.** AI output is never presented as final;
   every output is checked against the source artifact before being handed
   to a human reviewer.
3. **Human-in-the-loop by design**, not an afterthought — positioned as an
   AI co-pilot for modernization teams, not an autonomous migration engine.
4. **Provider-agnostic.** The framework isn't built around one vendor's LLM
   or one migration tool; it's designed to plug in whichever model/tool
   fits the organization's existing stack.

This framework is not intended to replace tools like SnowConvert — in a real
deployment, it could sit *around* such a tool, using its output as an
additional input to the AI Analysis Layer for documentation and rule
extraction.

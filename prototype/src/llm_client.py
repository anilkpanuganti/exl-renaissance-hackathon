"""
llm_client.py
--------------
Provider-agnostic LLM client for the GenAI-Assisted Modernization Framework.

Supports:
  - Anthropic Claude (if ANTHROPIC_API_KEY is set)
  - OpenAI GPT models (if OPENAI_API_KEY is set)
  - Mock mode (no key required) - uses deterministic heuristics so the
    full pipeline is runnable and demoable without any API key or
    network access. This also doubles as a fallback / cost-control path
    referenced in docs/architecture.md (cost & latency considerations).

Design rationale is documented in docs/prompt-engineering.md.
"""

import json
import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str


class LLMClient:
    """Thin wrapper that picks a provider based on available env vars."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or self._detect_provider()
        self.model = model or self._default_model(self.provider)

    def _detect_provider(self) -> str:
        if os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        return "mock"

    def _default_model(self, provider: str) -> str:
        return {
            "anthropic": "claude-sonnet-5",
            "openai": "gpt-4o",
            "mock": "mock-heuristic-v1",
        }[provider]

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        if self.provider == "anthropic":
            return self._call_anthropic(system_prompt, user_prompt)
        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        return self._call_mock(system_prompt, user_prompt)

    # ------------------------------------------------------------------
    # Real providers (require the respective SDK + API key to actually run)
    # ------------------------------------------------------------------
    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        import anthropic  # requires: pip install anthropic

        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in msg.content if block.type == "text")
        return LLMResponse(text=text, provider="anthropic", model=self.model)

    def _call_openai(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        from openai import OpenAI  # requires: pip install openai

        client = OpenAI()
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = resp.choices[0].message.content
        return LLMResponse(text=text, provider="openai", model=self.model)

    # ------------------------------------------------------------------
    # Mock mode: deterministic heuristic extraction over the sample SQL.
    # This exists so judges/reviewers can run the full pipeline with
    # zero setup. It is intentionally simple regex/keyword logic, NOT a
    # simulation of an LLM's reasoning - clearly labeled as such in every
    # output artifact.
    # ------------------------------------------------------------------
    def _call_mock(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        if "EXTRACT" in system_prompt:
            text = self._mock_analysis(user_prompt)
        elif "TRANSFORM" in system_prompt:
            text = self._mock_transform(user_prompt)
        else:
            text = self._mock_docs(user_prompt)
        return LLMResponse(text=text, provider="mock", model=self.model)

    def _mock_analysis(self, sql_text: str) -> str:
        # Strip SQL line comments before structural regex matching, so
        # incidental English words in comments (e.g. "... from order_date
        # get an extra 2%") aren't mistaken for FROM/JOIN/INTO clauses.
        code_only = re.sub(r"--.*", "", sql_text)
        raw_matches = re.findall(
            r"(?:FROM|JOIN|INTO|MERGE INTO)\s+([a-zA-Z_][\w]*)",
            code_only, flags=re.IGNORECASE)
        # Known false-positive keywords that regex heuristics can pick up
        # (e.g. "UPDATE <table> SET" fragments). A real LLM call would not
        # need this list; it's specific to the deterministic mock mode.
        noise = {"set", "select", "values"}
        tables = sorted({t for t in raw_matches if t.lower() not in noise})

        rules = []
        if "CASE" in sql_text.upper() and "region_code" in sql_text:
            rules.append({
                "id": "AI-01", "name": "Customer Region Mapping",
                "description": "region_code mapped to a full region name via CASE statement.",
                "confidence": 0.95
            })
        if "lifetime_value" in sql_text:
            rules.append({
                "id": "AI-02", "name": "Customer Tier Classification",
                "description": "Customer tier derived from lifetime_value thresholds.",
                "confidence": 0.95
            })
        if "customer_tier" in sql_text and "0.15" in sql_text:
            rules.append({
                "id": "AI-03", "name": "Tier-Based Discount",
                "description": "Discount percentage applied based on customer_tier (PLATINUM/GOLD/SILVER/else).",
                "confidence": 0.9
            })
        if "0.02" in sql_text and "SYSDATE - o.order_date" in sql_text:
            rules.append({
                "id": "AI-04", "name": "Order Aging Discount Exception",
                "description": "Additional discount applied when order age exceeds 90 days.",
                "confidence": 0.6,
                "ambiguity_flag": True,
                "confidence_notes": "Business justification for the 90-day / 2% values is not present in the source script; flagged for human review rather than assumed."
            })
        if "order_status IN" in sql_text or "derived_status" in sql_text:
            rules.append({
                "id": "AI-05", "name": "Order Status Normalization",
                "description": "Raw status codes normalized into CANCELLED/FULFILLED/IN_PROGRESS/UNKNOWN buckets.",
                "confidence": 0.9
            })
        if "active_flag" in sql_text:
            rules.append({
                "id": "AI-06", "name": "Active Customer Filter",
                "description": "Only customers with active_flag = 'Y' are included.",
                "confidence": 0.95
            })
        if "ADD_MONTHS(SYSDATE, -24)" in sql_text:
            rules.append({
                "id": "AI-07", "name": "2-Year Order Window",
                "description": "Only orders within the last 24 months are processed.",
                "confidence": 0.55,
                "ambiguity_flag": True,
                "confidence_notes": "No documented business reason found for the 24-month cutoff; flagged for human review."
            })
        if "MERGE INTO" in sql_text.upper():
            rules.append({
                "id": "AI-08", "name": "Customer Dimension SCD Type 1",
                "description": "dim_customers refreshed via MERGE with overwrite semantics; no history retained.",
                "confidence": 0.85
            })

        result = {
            "tables": tables,
            "business_rules": rules,
            "dependencies": [
                "stg_customers depends on raw_customers",
                "stg_orders depends on raw_orders, raw_order_items, stg_customers",
                "fct_orders depends on stg_orders",
                "dim_customers depends on stg_customers",
            ],
        }
        return json.dumps(result, indent=2)

    def _mock_transform(self, analysis_json: str) -> str:
        return (
            "-- MOCK MODE: representative Snowflake/dbt transformation.\n"
            "-- See prototype/output/dbt_models/ for generated model files.\n"
            "Transformation generated using rule-based mock provider. "
            "Set ANTHROPIC_API_KEY or OPENAI_API_KEY for LLM-generated transformations."
        )

    def _mock_docs(self, combined_json: str) -> str:
        return (
            "MOCK MODE documentation stub. Set ANTHROPIC_API_KEY or OPENAI_API_KEY "
            "for full LLM-generated narrative documentation."
        )

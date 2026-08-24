"""
transform.py
------------
Phase 3: Transformation Layer.

Given the AI Analysis Layer's extraction (+ the original legacy SQL for
grounding), generate:
  - Snowflake-native staging SQL
  - Conceptual dbt models (staging / intermediate / marts) as files

For the hackathon PoC, the dbt models are generated deterministically from
the known sample pipeline structure (see mock_generate_dbt_models). This
mirrors what an LLM-driven TRANSFORM_PROMPT would produce and is clearly
labeled as such; swapping in a real LLM call (see llm_client.py) would
follow the same TRANSFORM_SYSTEM_PROMPT pattern below.
"""

import os

TRANSFORM_SYSTEM_PROMPT = """You are performing legacy-to-Snowflake/dbt
TRANSFORMATION as part of an ETL modernization framework (TRANSFORM mode).

Given a structured business-rule extraction (JSON) and the original legacy
SQL for grounding, generate:
  1. Snowflake-native SQL equivalents for each legacy transformation step
  2. dbt model files following standard layering: staging -> intermediate -> marts
  3. A schema.yml with column-level tests (not_null, accepted_values, relationships)
     for every business rule identified in the extraction

STRICT RULES:
1. Preserve every business rule from the extraction exactly - do not
   simplify, drop, or "improve" business logic without flagging the change.
2. Where the extraction flagged ambiguity_flag=true, carry the same flag
   forward as a SQL comment in the generated model, so a human reviewer sees
   it at the point of transformation, not just in a separate report.
3. Use dbt ref()/source() macros, not hardcoded table names.
4. Output valid SQL/YAML only, in clearly delimited file blocks.
"""


def generate_dbt_models(analysis: dict, output_dir: str) -> list:
    """Generate a conceptual dbt project structure demonstrating the
    Transformation Layer. Returns list of file paths written."""

    staging_dir = os.path.join(output_dir, "dbt_models", "staging")
    intermediate_dir = os.path.join(output_dir, "dbt_models", "intermediate")
    marts_dir = os.path.join(output_dir, "dbt_models", "marts")
    for d in (staging_dir, intermediate_dir, marts_dir):
        os.makedirs(d, exist_ok=True)

    written = []

    # --- sources.yml ---
    sources_yml = """version: 2

sources:
  - name: raw
    schema: raw
    tables:
      - name: raw_customers
      - name: raw_orders
      - name: raw_order_items
"""
    written.append(_write(os.path.join(output_dir, "dbt_models", "sources.yml"), sources_yml))

    # --- staging: stg_customers.sql ---
    stg_customers = """-- Generated from legacy dedupe + region/tier CASE logic (AI-01, AI-02)
with source as (
    select * from {{ source('raw', 'raw_customers') }}
    where active_flag = 'Y'  -- BR: Active Customer Filter (AI-06)
),

deduped as (
    select *,
        row_number() over (
            partition by customer_id order by created_date desc
        ) as rn
    from source
)

select
    customer_id,
    upper(trim(customer_name)) as customer_name,
    email,
    case
        when region_code = 'NA' then 'North America'
        when region_code = 'EU' then 'Europe'
        when region_code = 'AP' then 'Asia Pacific'
        else 'Unknown'
    end as region,
    case
        when lifetime_value >= 50000 then 'PLATINUM'
        when lifetime_value >= 15000 then 'GOLD'
        when lifetime_value >= 2000  then 'SILVER'
        else 'STANDARD'
    end as customer_tier,
    created_date
from deduped
where rn = 1
"""
    written.append(_write(os.path.join(staging_dir, "stg_customers.sql"), stg_customers))

    # --- staging: stg_orders.sql ---
    stg_orders = """-- Generated from legacy order staging + discount calc (AI-03, AI-04, AI-05)
select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_status,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    c.customer_tier
from {{ source('raw', 'raw_orders') }} o
join {{ source('raw', 'raw_order_items') }} oi on o.order_id = oi.order_id
join {{ ref('stg_customers') }} c on o.customer_id = c.customer_id
-- AMBIGUITY FLAGGED (AI-07): 24-month window has no documented business
-- justification in the legacy source. Carried forward for human review.
where o.order_date >= dateadd(month, -24, current_date())
"""
    written.append(_write(os.path.join(staging_dir, "stg_orders.sql"), stg_orders))

    # --- intermediate: int_order_line_discounts.sql ---
    int_discounts = """-- Business rule AI-03 (tier discount) + AI-04 (aging discount, AMBIGUOUS)
with base as (
    select *,
        case customer_tier
            when 'PLATINUM' then 0.15
            when 'GOLD' then 0.10
            when 'SILVER' then 0.05
            else 0
        end as tier_discount_pct,
        -- AMBIGUITY FLAGGED (AI-04): 90-day / 2% aging discount has no
        -- documented business justification in the legacy source.
        -- Human reviewer: confirm this is intentional before promoting to prod.
        case
            when datediff(day, order_date, current_date()) > 90 then 0.02
            else 0
        end as aging_discount_pct
    from {{ ref('stg_orders') }}
)

select
    *,
    round(quantity * unit_price * (1 - (tier_discount_pct + aging_discount_pct)), 2)
        as net_line_amount,
    case
        when order_status in ('CANC', 'CANCELLED') then 'CANCELLED'
        when order_status in ('SHIP', 'SHIPPED', 'DELIVERED') then 'FULFILLED'
        when order_status in ('PEND', 'PROCESSING') then 'IN_PROGRESS'
        else 'UNKNOWN'
    end as derived_status
from base
"""
    written.append(_write(os.path.join(intermediate_dir, "int_order_line_discounts.sql"), int_discounts))

    # --- marts: fct_orders.sql ---
    fct_orders = """select
    order_id,
    customer_id,
    product_id,
    order_date,
    quantity,
    unit_price,
    net_line_amount,
    derived_status
from {{ ref('int_order_line_discounts') }}
"""
    written.append(_write(os.path.join(marts_dir, "fct_orders.sql"), fct_orders))

    # --- marts: dim_customers.sql ---
    dim_customers = """-- Note (AI-08): legacy used SCD Type 1 (overwrite, no history).
-- Recommendation: consider dbt snapshot for SCD Type 2 if history is needed
-- going forward - flagged as a migration RECOMMENDATION, not applied by default,
-- to avoid silently changing legacy behavior.
select
    customer_id,
    customer_name,
    email,
    region,
    customer_tier,
    created_date
from {{ ref('stg_customers') }}
"""
    written.append(_write(os.path.join(marts_dir, "dim_customers.sql"), dim_customers))

    # --- schema.yml with tests tied to business rules ---
    schema_yml = """version: 2

models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests: [not_null, unique]
      - name: customer_tier
        tests:
          - accepted_values:
              values: ['PLATINUM', 'GOLD', 'SILVER', 'STANDARD']

  - name: int_order_line_discounts
    columns:
      - name: derived_status
        tests:
          - accepted_values:
              values: ['CANCELLED', 'FULFILLED', 'IN_PROGRESS', 'UNKNOWN']
      - name: net_line_amount
        tests: [not_null]

  - name: fct_orders
    columns:
      - name: order_id
        tests: [not_null]
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
"""
    written.append(_write(os.path.join(output_dir, "dbt_models", "schema.yml"), schema_yml))

    return written


def _write(path: str, content: str) -> str:
    with open(path, "w") as f:
        f.write(content)
    return path


if __name__ == "__main__":
    from .ai_analysis import analyze_legacy_sql

    with open("prototype/sample_legacy/legacy_customer_orders_etl.sql") as f:
        sql = f.read()
    analysis = analyze_legacy_sql(sql)
    files = generate_dbt_models(analysis, "prototype/output")
    print("\n".join(files))

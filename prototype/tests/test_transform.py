import os
from prototype.src.transform import generate_dbt_models


def test_generate_dbt_models_writes_files(tmp_path):
    out = str(tmp_path)
    analysis = {"tables": ["raw_customers", "raw_orders"], "business_rules": []}
    files = generate_dbt_models(analysis, out)
    # Verify expected files exist
    expected = [
        os.path.join(out, "dbt_models", "sources.yml"),
        os.path.join(out, "dbt_models", "staging", "stg_customers.sql"),
        os.path.join(out, "dbt_models", "staging", "stg_orders.sql"),
        os.path.join(out, "dbt_models", "intermediate", "int_order_line_discounts.sql"),
        os.path.join(out, "dbt_models", "marts", "fct_orders.sql"),
        os.path.join(out, "dbt_models", "marts", "dim_customers.sql"),
        os.path.join(out, "dbt_models", "schema.yml"),
    ]
    for e in expected:
        assert os.path.exists(e)
    # and returned list should contain those paths
    for e in expected:
        assert e in files

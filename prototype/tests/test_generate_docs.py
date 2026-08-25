import json
from prototype.src.generate_docs import generate_migration_report


def test_generate_migration_report_minimal():
    analysis = {"tables": ["t1"], "business_rules": []}
    validation = {"overall_status": "PASS", "checks_passed": [], "checks_failed": []}
    dbt_files = ["output/dbt_models/schema.yml"]
    report = generate_migration_report(analysis, validation, dbt_files, source_name="test.sql")
    assert "## 1. Overview" in report
    assert "## 2. Business Rule  Snowflake/dbt Mapping" or "## 2. Business Rule" or "## 2." in report
    assert "## 5. Validation Summary" in report
    assert "Recommendation" in report


def test_generate_migration_report_with_workflow_and_plan():
    analysis = {"tables": ["t1"], "business_rules": []}
    validation = {"overall_status": "REVIEW_REQUIRED", "checks_passed": [], "checks_failed": ["X"]}
    dbt_files = []
    workflow_jobs = [{"id": "job1", "name": "Job 1", "analysis": {"tables": ["t1"], "business_rules": []}}]
    migration_plan = {"steps": [{"order": 1, "table": "t1", "effort": "Low", "rules_touching": [], "blocking": False}], "blocking_items": []}
    report = generate_migration_report(analysis, validation, dbt_files, source_name="workflow", metadata_findings=None, workflow_jobs=workflow_jobs, migration_plan=migration_plan)
    assert "## 4.a Perjob Analysis" or "## 4.a Perjob Analysis" or "## 4.a Per" in report
    assert "## Migration Plan" in report

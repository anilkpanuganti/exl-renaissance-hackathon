# Workflow: inventory_sync_workflow

This sample models a legacy multi-job batch workflow (3 steps) that might
have been orchestrated by Informatica, Control‑M, or a shell scheduler.
It demonstrates cross-job dependencies, implicit business rules embedded
in transformation logic, and the kind of manifest artifacts an
orchestration engine would produce.

Files in this folder:
- manifest.json — workflow manifest listing job order, scheduling info and dependencies
- job1_extract_inventory.sql — extracts raw feed rows into staging (dedupe)
- job2_transform_inventory.sql — transforms quantities, applies promotional shrinkage and recency filter
- job3_sync_inventory.sql — merges transformed rows into reporting store and queues an indexing command
- ground_truth_rules.json — hand-annotated ground truth rules for PoC evaluation

Scenario notes:
- The workflow runs nightly at 02:00 UTC.
- Two intentionally undocumented/ambiguous rules are present: a 10% shrinkage for 'PROMO' category items, and an 18-month recency cutoff for items to be considered active. These mirror real-world legacy exceptions that are often undocumented and must be surfaced during modernization.

This sample is intended for PoC evaluation only and is not connected to the main pipeline by default. Wiring it into the orchestration for automated runs is a follow-up task.

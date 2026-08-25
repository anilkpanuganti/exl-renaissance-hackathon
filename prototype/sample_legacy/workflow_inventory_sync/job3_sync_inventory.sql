-- =============================================================
-- JOB: job3_sync (Merge transformed inventory into reporting store)
-- Platform: Oracle PL/SQL-style batch SQL (representative)
-- =============================================================

MERGE INTO rpt_inventory d
USING stg_inventory_transformed s
ON (d.sku = s.sku)
WHEN MATCHED THEN
  UPDATE SET
    d.sku_desc = s.sku_desc,
    d.category = s.category_code,
    d.available_qty = s.available_qty,
    d.last_sold_date = s.last_sold_date,
    d.discontinued = s.discontinued_flag
WHEN NOT MATCHED THEN
  INSERT (sku, sku_desc, category, available_qty, last_sold_date, discontinued)
  VALUES (s.sku, s.sku_desc, s.category_code, s.available_qty, s.last_sold_date, s.discontinued_flag);

-- After sync, trigger downstream indexing job via a legacy command table entry
INSERT INTO ctl_commands (cmd, created_at) VALUES ('INDEX-RPT-INVENTORY', SYSDATE);

COMMIT;

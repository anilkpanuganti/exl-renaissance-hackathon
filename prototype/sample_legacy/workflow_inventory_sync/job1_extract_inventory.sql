-- =============================================================
-- JOB: job1_extract (Extract raw inventory into staging)
-- Platform: Oracle PL/SQL-style batch SQL (representative)
-- Sparse comments to mimic legacy assets
-- =============================================================

-- Create/refresh staging inventory from raw feed
DELETE FROM stg_inventory a
WHERE ROWID NOT IN (
  SELECT MAX(ROWID)
  FROM stg_inventory b
  WHERE a.sku = b.sku
);

INSERT INTO stg_inventory
SELECT
  r.sku,
  r.sku_desc,
  r.category_code,
  r.on_hand_qty,
  r.reserved_qty,
  r.last_sold_date,
  -- NOTE: legacy feed stores flagged discontinued as 'Y' occasionally
  r.discontinued_flag
FROM raw_inventory r
WHERE r.source = 'LEGACY_FEED';

COMMIT;

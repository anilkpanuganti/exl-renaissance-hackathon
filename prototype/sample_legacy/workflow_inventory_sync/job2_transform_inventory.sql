-- =============================================================
-- JOB: job2_transform (Transform quantities and compute available stock)
-- Platform: Oracle PL/SQL-style batch SQL (representative)
-- =============================================================

-- Calculate available_qty and apply business rules
INSERT INTO stg_inventory_transformed
SELECT
  s.sku,
  s.sku_desc,
  s.category_code,
  s.on_hand_qty,
  s.reserved_qty,
  -- available = on_hand - reserved, but for PROMO category apply 10% reduction
  -- (undocumented business exception: promotional inventory subject to 10% shrinkage)
  ROUND((s.on_hand_qty - s.reserved_qty) *
    (CASE WHEN s.category_code = 'PROMO' THEN 0.90 ELSE 1 END)
  , 0) AS available_qty,
  s.last_sold_date,
  s.discontinued_flag
FROM stg_inventory s
WHERE (s.on_hand_qty - s.reserved_qty) > 0
  AND s.discontinued_flag <> 'Y'
  -- business filter: only items sold in the last 18 months are considered active
  AND s.last_sold_date >= ADD_MONTHS(SYSDATE, -18);

COMMIT;

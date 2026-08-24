-- =============================================================
-- LEGACY ETL: sp_load_customer_orders
-- Original platform: Oracle PL/SQL (representative / conceptual sample)
-- Last known modification: unknown (no version history retained)
-- Original author: unknown (tribal knowledge, not documented)
-- =============================================================
-- NOTE: comments below are exactly as found in the legacy system --
-- i.e. sparse and inconsistent. This is intentional for the PoC:
-- it demonstrates a realistic "poorly documented legacy asset."
-- =============================================================

CREATE OR REPLACE PROCEDURE sp_load_customer_orders AS
BEGIN

  -- step 1: dedupe raw customers, keep latest record per cust id
  DELETE FROM stg_customers a
  WHERE ROWID NOT IN (
    SELECT MAX(ROWID)
    FROM stg_customers b
    WHERE a.customer_id = b.customer_id
  );

  INSERT INTO stg_customers
  SELECT
    customer_id,
    UPPER(TRIM(customer_name)) AS customer_name,
    email,
    CASE
      WHEN region_code = 'NA' THEN 'North America'
      WHEN region_code = 'EU' THEN 'Europe'
      WHEN region_code = 'AP' THEN 'Asia Pacific'
      ELSE 'Unknown'
    END AS region,
    -- tier logic hardcoded, no doc on why these thresholds
    CASE
      WHEN lifetime_value >= 50000 THEN 'PLATINUM'
      WHEN lifetime_value >= 15000 THEN 'GOLD'
      WHEN lifetime_value >= 2000  THEN 'SILVER'
      ELSE 'STANDARD'
    END AS customer_tier,
    created_date
  FROM raw_customers
  WHERE active_flag = 'Y';

  -- step 2: order staging with discount calc (business rule embedded)
  INSERT INTO stg_orders
  SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_status,
    oi.product_id,
    oi.quantity,
    oi.unit_price,
    -- discount rule: platinum gets 15%, gold 10%, silver 5%, else 0
    -- also: orders over 90 days from order_date get an extra 2% "aging discount"
    -- (undocumented business exception, found only in this CASE block)
    ROUND(
      oi.quantity * oi.unit_price *
      (1 - (
        CASE c.customer_tier
          WHEN 'PLATINUM' THEN 0.15
          WHEN 'GOLD' THEN 0.10
          WHEN 'SILVER' THEN 0.05
          ELSE 0
        END
        +
        CASE WHEN (SYSDATE - o.order_date) > 90 THEN 0.02 ELSE 0 END
      ))
    , 2) AS net_line_amount,
    -- order status derivation, magic string comparisons
    CASE
      WHEN o.order_status IN ('CANC', 'CANCELLED') THEN 'CANCELLED'
      WHEN o.order_status IN ('SHIP', 'SHIPPED', 'DELIVERED') THEN 'FULFILLED'
      WHEN o.order_status IN ('PEND', 'PROCESSING') THEN 'IN_PROGRESS'
      ELSE 'UNKNOWN'
    END AS derived_status
  FROM raw_orders o
  JOIN raw_order_items oi ON o.order_id = oi.order_id
  JOIN stg_customers c ON o.customer_id = c.customer_id
  WHERE o.order_date >= ADD_MONTHS(SYSDATE, -24); -- only last 2 years, reason unclear

  -- step 3: curated fact table load
  INSERT INTO fct_orders
  SELECT
    order_id,
    customer_id,
    product_id,
    order_date,
    quantity,
    unit_price,
    net_line_amount,
    derived_status
  FROM stg_orders;

  -- step 4: dim_customers refresh (SCD type 1, overwrite - no history kept)
  MERGE INTO dim_customers d
  USING stg_customers s
  ON (d.customer_id = s.customer_id)
  WHEN MATCHED THEN
    UPDATE SET
      d.customer_name = s.customer_name,
      d.region = s.region,
      d.customer_tier = s.customer_tier
  WHEN NOT MATCHED THEN
    INSERT (customer_id, customer_name, email, region, customer_tier, created_date)
    VALUES (s.customer_id, s.customer_name, s.email, s.region, s.customer_tier, s.created_date);

  COMMIT;

EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE;
END sp_load_customer_orders;
/

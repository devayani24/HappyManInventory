-- ============================================================
-- V1: Initial schema
--
-- Purchasing system for a sweet shop. Records what arrives from
-- suppliers, and what is bought for cash from local shops.
--
-- Conventions used throughout:
--   Money is stored as integer paise. 520 rupees = 52000.
--   Nothing is deleted. Corrections set is_void with a timestamp
--     and a reason, so records stay auditable.
--   Rates are snapshotted onto delivery lines at save time and
--     never read back from a rate card, so a price change cannot
--     retrospectively revalue past deliveries.
--
-- Payment tracking is not in this version.
-- ============================================================


-- ============================================================
-- Reference data
-- Seeded once from seed_data.json. Changes rarely.
-- ============================================================

-- Grain: one company we buy from
CREATE TABLE suppliers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    local_name  TEXT,
    phone       TEXT,
    address     TEXT,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    UNIQUE (name),
    CHECK (is_active IN (0, 1))
);


-- Grain: one grouping of materials
-- Used to group the chips on the delivery entry screen.
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    local_name  TEXT,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    UNIQUE (name),
    CHECK (is_active IN (0, 1))
);


-- Grain: one raw material
-- base_unit is fixed per material, so every rate for that material
-- is comparable over time. Quantities are always entered in it.
CREATE TABLE materials (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id  INTEGER NOT NULL,
    name         TEXT    NOT NULL,
    local_name   TEXT,
    base_unit    TEXT    NOT NULL,
    is_active    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    FOREIGN KEY (category_id) REFERENCES categories(id),

    UNIQUE (name),
    CHECK (is_active IN (0, 1)),
    CHECK (base_unit IN ('g', 'kg', 'ml', 'L', 'piece', 'cylinder'))
);


-- Grain: one material sold by one supplier
--
-- Records the relationship only: who sells what, and whether we
-- still buy it. The rate is NOT stored here. It is derived from
-- the most recent non-voided delivery, so voiding a delivery
-- reverts the displayed rate with no code doing anything.
-- See v_supplier_material_rates.
CREATE TABLE supplier_materials (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id  INTEGER NOT NULL,
    material_id  INTEGER NOT NULL,
    is_active    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (material_id) REFERENCES materials(id),

    UNIQUE (supplier_id, material_id),
    CHECK (is_active IN (0, 1))
);


-- ============================================================
-- Transaction data
-- Grows with use. Written by the application, never seeded.
-- ============================================================

-- Grain: one delivery from one source on one date
--
-- source = 'supplier'  on account from a named company
--          'local'     cash purchase from a shop, no supplier
--
-- total is computed server-side from the lines, never sent by
-- the browser.
CREATE TABLE deliveries (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    source         TEXT    NOT NULL DEFAULT 'supplier',
    supplier_id    INTEGER,
    delivery_date  TEXT    NOT NULL DEFAULT (date('now','localtime')),
    invoice_no     TEXT,
    total          INTEGER NOT NULL,
    notes          TEXT,
    is_void        INTEGER NOT NULL DEFAULT 0,
    voided_at      TEXT,
    void_reason    TEXT,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),

    CHECK (source IN ('supplier', 'local')),
    CHECK (total > 0),
    CHECK (is_void IN (0, 1)),

    -- a supplier delivery names a supplier; a local one never does
    CHECK ((source = 'supplier' AND supplier_id IS NOT NULL)
        OR (source = 'local'    AND supplier_id IS NULL)),

    -- a void must carry both a timestamp and a reason, so a
    -- half-completed void cannot exist
    CHECK ((is_void = 0 AND voided_at IS NULL     AND void_reason IS NULL)
        OR (is_void = 1 AND voided_at IS NOT NULL AND void_reason IS NOT NULL))
);


-- Grain: one material on one delivery
--
-- This is the fact table. rate is what was actually paid on the
-- delivery date, frozen at save. quantity is always in the
-- material's base_unit, so rates are comparable across time.
CREATE TABLE delivery_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id  INTEGER NOT NULL,
    material_id  INTEGER NOT NULL,
    quantity     REAL    NOT NULL,
    unit         TEXT    NOT NULL,
    rate         INTEGER NOT NULL,
    line_total   INTEGER NOT NULL,

    FOREIGN KEY (delivery_id) REFERENCES deliveries(id),
    FOREIGN KEY (material_id) REFERENCES materials(id),

    CHECK (quantity > 0),
    CHECK (rate > 0),
    CHECK (line_total > 0)
);


-- ============================================================
-- Indexes
-- Foreign keys are not indexed automatically in SQLite, and
-- delivery_date is filtered on every list and export.
-- ============================================================

CREATE INDEX idx_materials_category      ON materials(category_id);
CREATE INDEX idx_sm_supplier             ON supplier_materials(supplier_id);
CREATE INDEX idx_deliveries_supplier     ON deliveries(supplier_id);
CREATE INDEX idx_deliveries_date         ON deliveries(delivery_date);
CREATE INDEX idx_delivery_items_delivery ON delivery_items(delivery_id);
CREATE INDEX idx_delivery_items_material ON delivery_items(material_id);


-- ============================================================
-- Views
--
-- Everything that reads delivery data goes through a view, so the
-- rule "voided rows never count" lives in one place and cannot be
-- forgotten by a caller.
-- ============================================================

-- Grain: one material on one delivery
--
-- Flat, denormalised, names included. Read by the Deliveries
-- screen, the Excel export, and ad-hoc analysis. Power Query
-- reads this rather than the tables, so the physical schema can
-- change without breaking the dashboard.
--
-- The supplier join is LEFT: a local purchase has no supplier,
-- and an inner join would silently drop every local row.
CREATE VIEW v_delivery_lines AS
SELECT
    di.id          AS line_id,
    d.id           AS delivery_id,
    d.delivery_date,
    d.invoice_no,
    d.source,
    CASE WHEN d.source = 'local' THEN 1 ELSE 0 END AS is_local_purchase,
    s.id           AS supplier_id,
    s.name         AS supplier_name,
    s.local_name   AS supplier_local_name,
    m.id           AS material_id,
    m.name         AS material_name,
    m.local_name   AS material_local_name,
    m.base_unit,
    c.id           AS category_id,
    c.name         AS category_name,
    c.local_name   AS category_local_name,
    di.quantity,
    di.unit,
    di.rate,
    di.line_total
FROM deliveries d
JOIN delivery_items di ON di.delivery_id = d.id
JOIN materials      m  ON m.id  = di.material_id
JOIN categories     c  ON c.id  = m.category_id
LEFT JOIN suppliers s  ON s.id  = d.supplier_id
WHERE d.is_void = 0;


-- Grain: one material sold by one supplier
--
-- The rate card for the entry screen and the Companies tab.
-- Driven from supplier_materials, so a pairing with no deliveries
-- still appears with a NULL rate - that means "not bought yet",
-- not "missing data".
--
-- last_paid_rate comes from the most recent non-voided delivery,
-- so it corrects itself when a delivery is voided.
CREATE VIEW v_supplier_material_rates AS
WITH latest_rate AS (
    SELECT
        supplier_id,
        material_id,
        rate,
        delivery_date,
        ROW_NUMBER() OVER (
            PARTITION BY supplier_id, material_id
            ORDER BY delivery_date DESC, line_id DESC
        ) AS rn
    FROM v_delivery_lines
)
SELECT
    sm.id,
    sm.supplier_id,
    sm.material_id,
    sm.is_active,
    m.name            AS material_name,
    m.local_name      AS material_local_name,
    m.base_unit,
    c.name            AS category_name,
    c.local_name      AS category_local_name,
    c.sort_order      AS category_sort_order,
    lr.rate           AS last_paid_rate,
    lr.delivery_date  AS rate_paid_on
FROM supplier_materials sm
JOIN materials  m ON m.id = sm.material_id
JOIN categories c ON c.id = m.category_id
LEFT JOIN latest_rate lr
       ON lr.supplier_id = sm.supplier_id
      AND lr.material_id = sm.material_id
      AND lr.rn = 1;
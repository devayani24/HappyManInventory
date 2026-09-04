

-- Table: suppliers
CREATE TABLE suppliers (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT NOT NULL,
   local_name TEXT,
   phone TEXT,
   address TEXT,
   delivery_cycle INTEGER,
   is_active INTEGER NOT NULL DEFAULT 1,
   created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
   
   UNIQUE (name),
   CHECK (is_active IN (0, 1))
   
);

-- Table: categories
-- Groups materials in the entry panel.
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



-- Table: materials
CREATE TABLE materials (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   category_id  INTEGER NOT NULL,
   name TEXT  NOT NULL,
   local_name TEXT,
   base_unit TEXT  NOT NULL,
   is_active INTEGER NOT NULL DEFAULT 1,
   created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
   
   FOREIGN KEY (category_id) REFERENCES categories(id),
   UNIQUE(name),
   CHECK (is_active IN (0, 1)),
   CHECK (base_unit IN ('g','kg','ml','L','piece','cylinder'))
);

-- Table: supplier_materials
CREATE TABLE supplier_materials (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	supplier_id INTEGER  NOT NULL,
	material_id INTEGER  NOT NULL,
	last_rate INTEGER,
	is_active INTEGER NOT NULL DEFAULT 1,
	rate_updated_on TEXT,
	created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),

	FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
	FOREIGN KEY (material_id) REFERENCES materials(id),

	UNIQUE(supplier_id,material_id),
	CHECK (last_rate IS NULL OR last_rate > 0),
	CHECK (is_active IN (0,1))
);


-- Table: deliveries
CREATE TABLE deliveries (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	source TEXT NOT NULL DEFAULT 'supplier',
	supplier_id INTEGER,
	delivery_date TEXT NOT NULL DEFAULT (date('now','localtime')),
	invoice_no TEXT,
	total INTEGER  NOT NULL,
	notes TEXT,
	is_void INTEGER NOT NULL DEFAULT 0 ,
	voided_at TEXT,
	void_reason TEXT,
	created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),

	FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
	
	CHECK (source IN ('supplier', 'local')),
	CHECK (total > 0),
	CHECK (is_void IN (0, 1)),
	
	CHECK ((is_void = 0 AND voided_at IS NULL AND void_reason IS NULL)
    OR (is_void = 1 AND voided_at IS NOT NULL AND void_reason IS NOT NULL)),
	
	-- a supplier delivery names a supplier; a local one never does
	CHECK ((source = 'supplier' AND supplier_id IS NOT NULL)
	OR (source = 'local' AND supplier_id IS NULL))
);

-- Table: delivery_items
-- material_id is always set.
-- supplier_material_id is set only when the line came off a rate card.
-- rate is snapshotted at save and never read back from the rate card.
CREATE TABLE delivery_items (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	delivery_id INTEGER  NOT NULL,
	material_id INTEGER NOT NULL,
	supplier_material_id INTEGER,
	quantity REAL  NOT NULL,
	unit TEXT  NOT NULL,
	rate INTEGER  NOT NULL,
	line_total INTEGER  NOT NULL,

	FOREIGN KEY (delivery_id) REFERENCES deliveries(id),
	FOREIGN KEY (material_id)          REFERENCES materials(id),
	FOREIGN KEY (supplier_material_id) REFERENCES supplier_materials(id),
	
	CHECK (quantity > 0),
	CHECK (rate > 0),
	CHECK (line_total > 0)
	
);



-- Table: Payments
-- A local purchase gets its payment row written in the same transaction
-- as the delivery, so outstanding is zero and it never reaches Payments due.

CREATE TABLE payments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	delivery_id INTEGER  NOT NULL,
	amount INTEGER  NOT NULL,
	paid_on TEXT NOT NULL DEFAULT (date('now','localtime')),
	method TEXT  NOT NULL,
	batch_id TEXT,
	notes TEXT,
	is_void INTEGER NOT NULL DEFAULT 0,
	voided_at TEXT,
	void_reason TEXT,
	created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),

	FOREIGN KEY(delivery_id) REFERENCES deliveries(id),
	
	CHECK (amount > 0),
	CHECK (method IN ('online', 'cash')),
	
	CHECK ((is_void = 0 AND voided_at IS NULL AND void_reason IS NULL)
    OR (is_void = 1 AND voided_at IS NOT NULL AND void_reason IS NOT NULL))
 
);

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX idx_materials_category      ON materials(category_id);
CREATE INDEX idx_delivery_items_delivery ON delivery_items(delivery_id);
CREATE INDEX idx_delivery_items_material ON delivery_items(material_id);
CREATE INDEX idx_payments_delivery       ON payments(delivery_id);
CREATE INDEX idx_deliveries_supplier     ON deliveries(supplier_id);
CREATE INDEX idx_deliveries_date         ON deliveries(delivery_date);
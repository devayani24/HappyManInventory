import pytest
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger("tests.conftest")

MIGRATIONS_DIR = Path(__file__).parent.parent/"app/db/migrations"

@pytest.fixture
def conn():
  """A fresh in-memory database with the schema applied and
    minimal reference data. Each test gets its own."""
  c = sqlite3.connect(":memory:")
  c.row_factory = sqlite3.Row
  c.execute("PRAGMA foreign_keys = ON")

  for path in sorted(MIGRATIONS_DIR.glob('V*__*.sql')):
    schema_sql = path.read_text(encoding='utf-8')
    c.executescript(schema_sql)

    logger.debug("[ok] applied %s", path.name)

  # minimal fixtures every test needs
  c.execute("INSERT INTO categories (name, sort_order) VALUES ('Test Category', 1)")
  c.execute("INSERT INTO suppliers (name) VALUES ('Ravi')")
  c.execute("INSERT INTO materials (category_id, name, base_unit) VALUES (1, 'material_1', 'kg')")
  c.execute("INSERT INTO materials (category_id, name, base_unit) VALUES (1, 'material_2', 'kg')")
  c.execute("INSERT INTO supplier_materials (supplier_id, material_id) VALUES (1, 1)")
  c.execute("INSERT INTO supplier_materials (supplier_id, material_id) VALUES (1, 2)")

  try:
        yield c  # Hands the live database to your test/script
  finally:
      c.close()  # Safely cleans up AFTER the test/script finishes

@pytest.fixture
def supplier_delivery(conn):
    conn.execute("INSERT INTO deliveries (source, supplier_id, total) VALUES ('supplier', 1, 10000)")
    conn.execute(
        "INSERT INTO delivery_items (delivery_id, material_id, quantity, unit, rate, line_total) VALUES (1, 1, 100, 'kg', 100, 10000)"
    )
    conn.execute(
            "INSERT INTO delivery_items (delivery_id, material_id, quantity, unit, rate, line_total) VALUES (1, 2, 5, 'kg', 20000, 100000)"
        )
    return 1

@pytest.fixture
def local_delivery(conn):
    conn.execute("INSERT INTO deliveries (source, total) VALUES ('local',10000)")
    conn.execute(
        "INSERT INTO delivery_items (delivery_id, material_id, quantity, unit, rate, line_total) VALUES (1, 1, 100, 'kg', 100, 10000)"
    )
    return 1

# @pytest.fixture
# def supplier_two_delivery(conn,supplier_delivery):
#     # conn.execute("INSERT INTO deliveries (source, supplier_id, total) VALUES ('supplier', 1, 10000)")
#     conn.execute(
        
                  
#         "INSERT INTO delivery_items (delivery_id, material_id, quantity, unit, rate, line_total) VALUES (1, 1, 5, 'kg', 20000, 100000)"
#     )

@pytest.fixture
def second_supplier_delivery(conn,supplier_delivery):
    conn.execute("INSERT INTO deliveries (source, supplier_id, total) VALUES ('supplier', 1, 30000)")
    conn.execute(
        "INSERT INTO delivery_items (delivery_id, material_id, quantity, unit, rate, line_total) VALUES (2, 1, 100, 'kg', 300, 30000)"
    )
    return 1

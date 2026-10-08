import sqlite3
import pytest

# --- materials:
 
 
def test_material_with_unknown_category_rejected(conn):
  with pytest.raises(sqlite3.IntegrityError):
      conn.execute(
          "INSERT INTO materials (name, category_id, base_unit) "
          "VALUES ('Ghost Sugar', 99999, 'kg')"
      )

# --- deliveries: 

def test_foreign_keys_are_enforced(conn):
  """If this fails, PRAGMA foreign_keys is not taking effect and
  every foreign key in the schema is decorative."""
  with pytest.raises(sqlite3.IntegrityError):
    conn.execute(
        "INSERT INTO deliveries(source,supplier_id,total) VALUES('supplier', 999, 10000)"
        )

def test_local_delivery_naming_a_supplier_rejected(conn):
  with pytest.raises(sqlite3.IntegrityError):
    conn.execute(
        "INSERT INTO deliveries (source, supplier_id, total) VALUES ('local', 1, 10000)"
        )

def test_supplier_delivery_without_supplier_rejected(conn):
  with pytest.raises(sqlite3.IntegrityError):
      conn.execute(
          "INSERT INTO deliveries (source, total) "
          "VALUES ('supplier', 10000)"
      )

# --- deliveries: the void contract ---------------------------------------
 
 
def test_void_without_reason_rejected(conn, supplier_delivery):
 
  with pytest.raises(sqlite3.IntegrityError):
      conn.execute(
          "UPDATE deliveries SET is_void = 1, voided_at = date('now') WHERE id = 1"
      )
def test_void_without_timestamp_rejected(conn, supplier_delivery):
  with pytest.raises(sqlite3.IntegrityError):
      conn.execute(
          "UPDATE deliveries SET is_void = 1, void_reason = 'wrong rate' WHERE id = 1"
      )

def test_voided_delivery_still_exists_in_the_table(conn, supplier_delivery):

  conn.execute(
      "UPDATE deliveries SET is_void = 1, voided_at = date('now'), "
      "void_reason = 'wrong rate' WHERE id = 1"
  )

  row = conn.execute(
      "SELECT COUNT(*) FROM deliveries WHERE id = 1"
  ).fetchone()


  assert row[0] == 1

def test_voided_delivery_not_in_v_delivery_lines(conn, supplier_delivery):

  conn.execute(
      "UPDATE deliveries SET is_void = 1, voided_at = date('now'), "
      "void_reason = 'wrong rate' WHERE id = 1"
  )

  row = conn.execute(
          "SELECT COUNT(*) FROM v_delivery_lines"
      ).fetchone()

  assert row[0] == 0

def test_voided_delivery_keeps_its_items(conn, supplier_delivery):
  conn.execute(
      "UPDATE deliveries SET is_void = 1, voided_at = date('now'), "
      "void_reason = 'wrong rate' WHERE id = 1"
  )

  row = conn.execute(
      "SELECT COUNT(*) FROM delivery_items WHERE delivery_id = 1"
  ).fetchone()

  assert row[0] == 2

def test_void_reason_on_live_delivery_rejected(conn, supplier_delivery):
    """Void columns travel together in both directions."""
 
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "UPDATE deliveries SET void_reason = 'wrong rate' WHERE id = 1"
        )

# --- delivery_items 

def test_item_with_unknown_material_rejected(conn):
   
  with pytest.raises(sqlite3.IntegrityError):
      conn.execute(
          "INSERT INTO delivery_items "
          "(delivery_id, material_id, quantity, unit, rate, line_total) "
          "VALUES (1, 99999, 1, 'kg', 10000, 10000)"
      )
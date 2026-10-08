import sqlite3
import pytest

def test_live_delivery_appears_in_lines_view(conn, supplier_delivery):
 
    row = conn.execute("SELECT count(distinct(delivery_id)) FROM v_delivery_lines").fetchone()
 
    assert row[0] == 1
 
 
def test_voided_delivery_excluded_from_lines_view(conn, supplier_delivery):
    conn.execute(
        "UPDATE deliveries SET is_void = 1, voided_at = '2026-10-02', "
        "void_reason = 'wrong rate' WHERE id = 1"
    )
 
    rows = conn.execute("SELECT * FROM v_delivery_lines").fetchall()
 
    assert rows == []


def test_local_purchase_appears_in_lines_view(conn, local_delivery):
 
    rows = conn.execute("SELECT * FROM v_delivery_lines").fetchall()
 
    assert len(rows) == 1
 
 
def test_local_purchase_has_no_supplier_name(conn, local_delivery):
 
    row = conn.execute("SELECT supplier_name FROM v_delivery_lines").fetchone()
 
    assert row["supplier_name"] is None
 
 
def test_local_purchase_is_flagged(conn, local_delivery):
 
    row = conn.execute("SELECT is_local_purchase FROM v_delivery_lines").fetchone()
 
    assert row["is_local_purchase"] == 1
 
 
def test_supplier_delivery_is_not_flagged_local(conn, supplier_delivery):
 
    row = conn.execute("SELECT is_local_purchase FROM v_delivery_lines").fetchone()
 
    assert row["is_local_purchase"] == 0
 
 
def test_lines_view_carries_the_category(conn, supplier_delivery):
 
    row = conn.execute("SELECT category_name FROM v_delivery_lines").fetchone()
 
    assert row["category_name"] == "Test Category"
 
 
def test_lines_view_grain_is_one_row_per_item(conn, supplier_delivery):
    """Two materials on one delivery is two rows, not one."""
   
    
 
    rows = conn.execute("SELECT * FROM v_delivery_lines").fetchall()
 
    assert len(rows) == 2

# --- v_supplier_material_rates -------------------------------------------
 
 
def test_pairing_with_no_deliveries_has_null_rate(conn):
    """The row exists; the rate is simply unknown.
 
    A missing row would break the entry screen — the material would vanish
    from the chip grid until someone bought it, which is backwards.
    """
    row = conn.execute(
        "SELECT last_paid_rate FROM v_supplier_material_rates WHERE id = 1"
    ).fetchone()
 
    assert row["last_paid_rate"] is None
 
 
def test_pairing_with_no_deliveries_still_appears(conn):
    rows = conn.execute(
        "SELECT * FROM v_supplier_material_rates WHERE id = 1"
    ).fetchall()
 
    assert len(rows) == 1
 
 
def test_rate_comes_from_the_delivery(conn, supplier_delivery):
 
    row = conn.execute(
        "SELECT last_paid_rate FROM v_supplier_material_rates WHERE id = 1"
    ).fetchone()
 
    assert row["last_paid_rate"] == 100
 
 
def test_rate_comes_from_the_latest_delivery(conn, second_supplier_delivery):
 
    row = conn.execute(
        "SELECT last_paid_rate FROM v_supplier_material_rates WHERE id = 1"
    ).fetchone()
 
    assert row["last_paid_rate"] == 300

 
 
def test_voiding_reverts_the_rate(conn, second_supplier_delivery):
    """The test that justifies the whole derived-rate design.
 
    No code updates a rate on void. The view recalculates and the old rate
    returns on its own. If this fails, rates have to be maintained by hand.
    """

    conn.execute(
        "UPDATE deliveries SET is_void = 1, voided_at = date('now'), "
        "void_reason = 'typed the rate wrong' WHERE id = 2"
    )
 
    row = conn.execute(
        "SELECT last_paid_rate FROM v_supplier_material_rates WHERE id = 1"
    ).fetchone()
 
    assert row["last_paid_rate"] == 100
 
 
def test_voiding_the_only_delivery_returns_a_null_rate(
    conn, supplier_delivery
):
    
    conn.execute(
        "UPDATE deliveries SET is_void = 1, voided_at = date('now'), "
        "void_reason = 'never arrived' WHERE id = 1"
    )
 
    row = conn.execute(
        "SELECT last_paid_rate FROM v_supplier_material_rates WHERE id = 1"
    ).fetchone()
 
    assert row[0] is None
 
 

 
 
def test_local_purchase_does_not_set_a_rate(conn, local_delivery):
    """A local purchase has no supplier, so it cannot belong to a rate card."""
    
    row = conn.execute(
        "SELECT last_paid_rate FROM v_supplier_material_rates WHERE id = 1"
    ).fetchone()
 
    assert row["last_paid_rate"] is None
 
 
def test_inactive_pairing_still_appears_in_the_view(conn):
    """The view carries is_active; filtering is the caller's job.
 
    The entry screen filters to active. The Companies screen shows both,
    so a deactivated material can be switched back on.
    """
    conn.execute("UPDATE supplier_materials SET is_active = 0 WHERE id = 1")
 
    row = conn.execute(
        "SELECT is_active FROM v_supplier_material_rates WHERE id = 1").fetchone()
 
    assert row["is_active"] == 0
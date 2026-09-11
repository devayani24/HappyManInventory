import json
from app.config import SEED_DATA_PATH, DATABASE_PATH, SCHEMA_PATH
import sqlite3
from contextlib import contextmanager
import logging

logger = logging.getLogger("app.db.setup_db") 

def load_seed():
  logger.debug("Reading seed file %s", SEED_DATA_PATH)
  with open(SEED_DATA_PATH, encoding="utf-8") as f:
    seed = json.load(f)
  logger.debug(
        "Seed contains %d categories, %d suppliers, %d materials, %d links",
        len(seed["categories"]), len(seed["suppliers"]),
        len(seed["materials"]), len(seed["supplier_materials"]),
    )
  return seed


def validate(seed):
  """Check every name reference resolves. Reports all problems at once.
     Set is prefered to list to avoid duplicates"""
  category_names = {c["name"] for c in seed["categories"]}
  supplier_names = {s["name"] for s in seed["suppliers"]}
  material_names = {m["name"] for m in seed["materials"]}

  problems = []

  for m in seed["materials"]:
        if m["category"] not in category_names:
            problems.append(
                f"material '{m['name']}' has unknown category '{m['category']}'"
            )

  for sm in seed["supplier_materials"]:
      if sm["supplier"] not in supplier_names:
          problems.append(f"unknown supplier '{sm['supplier']}'")
      if sm["material"] not in material_names:
          problems.append(f"unknown material '{sm['material']}'")

  

  for key in ("categories", "suppliers", "materials"):
        names = [x["name"] for x in seed[key]]
        for name in set(names):
           if names.count(name)>1:
              problems.append(f"duplicate {key[:-1]} name '{name}'")

  if problems:
      for p in problems:
            logger.error("seed validation: %s", p)
      raise ValueError(
        f"{len(problems)} bad reference(s) in seed_data.json:\n  "
        + "\n  ".join(problems)
      )
  logger.info("Seed data is valid")

@contextmanager
def get_connection():
    logger.debug("Opening connection to %s", DATABASE_PATH)
    conn = sqlite3.connect(DATABASE_PATH)
    # rows accessible by column name
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
        logger.debug("Transaction committed")
    except Exception:
        conn.rollback()
        logger.exception("Transaction rolled back")
        raise
    finally:
        conn.close()
        logger.debug("Connection closed")

def get_schema_path():
    return SCHEMA_PATH


def init_schema(conn):
    """Create tables from schema.sql."""
    schema_path = get_schema_path()
    schema_sql = schema_path.read_text(encoding='utf-8')

    
    conn.executescript(schema_sql)
    logger.info("Schema initialized at %s", DATABASE_PATH)


def seed_categories(conn, seed):
    categories = seed["categories"]
    cursor = conn.cursor()

    inserted = 0
    for c in categories:
        cursor.execute(
        """
        INSERT OR IGNORE INTO categories(name,local_name,sort_order) 
        VALUES(?,?,?) 
        """,
        (c["name"],c.get("local_name") or None,c["sort_order"])
        )
        inserted += cursor.rowcount

    cursor.execute("SELECT id, name FROM categories")
    category_ids = {row["name"]: row["id"] for row in cursor.fetchall()}

    report_seed("supplier_materials", len(categories), inserted)
    return category_ids

def seed_suppliers(conn, seed):
    suppliers = seed["suppliers"]
    cursor = conn.cursor()

    inserted = 0
    for s in suppliers:
        cursor.execute(
        """
        INSERT OR IGNORE INTO suppliers(name,local_name) 
        VALUES(?,?) 
        """,
        (s["name"],s.get("local_name") or None)
        )
        inserted += cursor.rowcount

    cursor.execute("SELECT id, name FROM suppliers")
    supplier_ids = {row["name"]: row["id"] for row in cursor.fetchall()}

    report_seed("supplier_materials", len(suppliers), inserted)
    return supplier_ids

def seed_materials(conn, seed, category_ids):
    materials = seed['materials']
    cursor = conn.cursor()

    inserted = 0
    for m in materials:
        cursor.execute(
        """
        INSERT OR IGNORE INTO materials(category_id,name,local_name,base_unit) 
        VALUES(?,?,?,?) 
        """,
        (category_ids[m["category"]], m["name"], m.get("local_name") or None, m["base_unit"])
        )
        inserted += cursor.rowcount

    cursor.execute("SELECT id, name FROM materials")
    material_ids = {row["name"]: row["id"] for row in cursor.fetchall()}
       
    report_seed("supplier_materials", len(materials), inserted)
    return material_ids

def seed_supplier_materials(conn, seed, supplier_ids,material_ids):
    supplier_materials = seed['supplier_materials']
    
    cursor = conn.cursor()

    inserted = 0
    for sm in supplier_materials:

        cursor.execute(
        """
        INSERT OR IGNORE INTO supplier_materials(supplier_id, material_id) 
        VALUES(?,?) 
        """,
        (supplier_ids[sm["supplier"]], material_ids[sm["material"]])
        )
        inserted += cursor.rowcount
    
    report_seed("supplier_materials", len(supplier_materials), inserted)

def report_seed(table, attempted, inserted):
    skipped = attempted - inserted
    if attempted == 0:
        logger.warning("%s: seed file has no rows", table)
    elif inserted == 0:
        logger.warning("%s: nothing inserted, all %d rows already present",
                       table, attempted)
    elif skipped:
        logger.warning("%s: inserted %d, skipped %d already present",
                       table, inserted, skipped)
    else:
        logger.info("%s: seeded %d rows", table, inserted)

def setup():
    """Run the full database initialization."""

    logger.info("Setting up database at %s", DATABASE_PATH)
    
    seed = load_seed()
    validate(seed)

    with get_connection() as conn:
        init_schema(conn)
        category_ids = seed_categories(conn, seed)
        supplier_ids = seed_suppliers(conn, seed)
        material_ids = seed_materials(conn, seed, category_ids)
        seed_supplier_materials(conn, seed, supplier_ids, material_ids)

    logger.info("Database setup complete")

    
  
# temporary
if __name__ == "__main__":
  from app.logger import configure_logging
  configure_logging()
  setup()
import json
from app.config import SEED_DATA_PATH, DATABASE_PATH, SCHEMA_PATH
import sqlite3
from contextlib import contextmanager

from datetime import datetime

def load_seed():
  with open(SEED_DATA_PATH, encoding="utf-8") as f:
    return json.load(f)


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
      raise ValueError(
        f"{len(problems)} bad reference(s) in seed_data.json:\n  "
        + "\n  ".join(problems)
      )

@contextmanager
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    # rows accessible by column name
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_schema_path():
    return SCHEMA_PATH


def init_schema(conn):
    """Create tables from schema.sql."""
    schema_path = get_schema_path()
    schema_sql = schema_path.read_text(encoding='utf-8')

    
    conn.executescript(schema_sql)
    print(f"✓ Database initialized at {DATABASE_PATH}")


def seed_categories(conn, seed):
    categories = seed["categories"]
    
    cursor = conn.cursor()
    category_ids = {}

    for c in categories:
        cursor.execute(
        """
        INSERT INTO categories(name,local_name,sort_order) 
        VALUES(?,?,?) 
        """,
        (c["name"],c.get("local_name") or None,c["sort_order"])
        )
        category_ids[c["name"]] = cursor.lastrowid
    print(f"✓ Seeded {len(categories)} categories")
    return category_ids

def seed_suppliers(conn, seed):
    suppliers = seed["suppliers"]
    
    cursor = conn.cursor()
    supplier_ids = {}

    for s in suppliers:
        cursor.execute(
        """
        INSERT INTO suppliers(name,local_name) 
        VALUES(?,?) 
        """,
        (s["name"],s.get("local_name") or None)
        )
        supplier_ids[s["name"]] = cursor.lastrowid
    print(f"✓ Seeded {len(suppliers)} suppliers")
    return supplier_ids

def seed_materials(conn, seed, category_ids):
    materials = seed['materials']

    cursor = conn.cursor()
    material_ids = {}

    for m in materials:
        cursor.execute(
        """
        INSERT INTO materials(category_id,name,local_name,base_unit) 
        VALUES(?,?,?,?) 
        """,
        (category_ids[m["category"]], m["name"], m.get("local_name") or None, m["base_unit"])
        )
        material_ids[m["name"]] = cursor.lastrowid
    print(f"✓ Seeded {len(materials)} materials")
    return material_ids

def seed_supplier_materials(conn, seed, supplier_ids,material_ids):
    supplier_materials = seed['supplier_materials']
    
    cursor = conn.cursor()
    for sm in supplier_materials:

        cursor.execute(
        """
        INSERT INTO supplier_materials(supplier_id, material_id) 
        VALUES(?,?) 
        """,
        (supplier_ids[sm["supplier"]], material_ids[sm["material"]])
        )
    print(f"✓ Seeded {len(supplier_materials)} supplier_materials")

def setup():
    """Run the full database initialization."""

    print(f"Setting up database at {DATABASE_PATH}")
    
    
    print(f"Load and Validate JSON seed data")
    seed = load_seed()
    validate(seed)
    print("[ok] seed data is valid")

    with get_connection() as conn:
        print("→ Initializing schema...")
        init_schema(conn)
        
        print(f"Load seed data into the database ...")
        category_ids = seed_categories(conn, seed)
        supplier_ids = seed_suppliers(conn, seed)
        material_ids = seed_materials(conn, seed, category_ids)
        seed_supplier_materials(conn, seed, supplier_ids, material_ids)

    
  
# temporary
if __name__ == "__main__":
  setup()
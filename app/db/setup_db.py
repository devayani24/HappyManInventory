import json
from app.config import SEED_DATA_PATH, DATABASE_PATH, SCHEMA_PATH
import sqlite3
from contextlib import contextmanager

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


def init_schema():
    """Create tables from schema.sql."""
    schema_path = get_schema_path()
    schema_sql = schema_path.read_text(encoding='utf-8')

    with get_connection() as conn:
        conn.executescript(schema_sql)
    print(f"✓ Database initialized at {DATABASE_PATH}")

def setup():
    """Run the full database initialization."""

    print(f"Setting up database at {DATABASE_PATH}")
    
    print("→ Initializing schema...")
    # init_schema()
    
    print(f"Load and Validate JOSN seed data")
    seed = load_seed()
    validate(seed)
    print("[ok] seed data is valid")

    
  
# temporary
if __name__ == "__main__":
  setup()
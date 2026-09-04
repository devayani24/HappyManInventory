from pathlib import Path

BASE_DIR = Path(__file__).parent.parent      #HappyManInventory
DATA_DIR = BASE_DIR/"data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR/ "inventory.db"
SEED_DATA_PATH = BASE_DIR/ "seed_data_private.json"
SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"
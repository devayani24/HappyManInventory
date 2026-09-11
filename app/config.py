from pathlib import Path

BASE_DIR = Path(__file__).parent.parent      #HappyManInventory
DATA_DIR = BASE_DIR/"data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
# LOG_DIR = BASE_DIR/"logs"
 

CONFIG_PATH = Path(__file__).with_name("logger_config.yaml")
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR/ "inventory.db"
SEED_DATA_PATH = BASE_DIR/ "seed_data_private.json"
SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"


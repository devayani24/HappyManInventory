from pathlib import Path

BASE_DIR = Path(__file__).parent.parent      #HappyManInventory
DATA_DIR = BASE_DIR/"data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UTILS_PATH = Path(__file__).parent / "utils"
 

CONFIG_PATH = UTILS_PATH / "logger_config.yaml"
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR/ "inventory.db"
SEED_DATA_PATH = BASE_DIR/ "seed_data_private.json"
SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"
MIGRATIONS_DIR = Path(__file__).parent / "db" / "migrations"


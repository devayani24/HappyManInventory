
import logging
import logging.config
from app.config import LOG_DIR,CONFIG_PATH

from yaml import safe_load

logger = logging.getLogger("app")

def configure_logging():
  with CONFIG_PATH.open(encoding="utf-8") as f:
    config = safe_load(f)

  # absolute path, so it doesn't depend on where you ran the command from
  config["handlers"]["rotating_file"]["filename"] = str(LOG_DIR / "app.log")

  logging.config.dictConfig(config)


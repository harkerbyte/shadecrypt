import os
from shadeDB.core import shadeDB

CONFIG_PATH = os.path.expanduser('~/.shadeDB/config.scdb')
CONFIG_DIR = os.path.dirname(CONFIG_PATH)
os.makedirs(CONFIG_DIR, exist_ok=True)

if not os.path.exists(CONFIG_PATH):
  with open(CONFIG_PATH, "w") as file:
    file.write("")  # optional: initial content
  os.chmod(CONFIG_PATH, 0o644)
  instance = shadeDB(CONFIG_PATH,write=True)
instance = shadeDB(CONFIG_PATH,write=True)
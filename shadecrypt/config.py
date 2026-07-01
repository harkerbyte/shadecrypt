import os
from shadecrypt.__init__ import instance,CONFIG_PATH

def load_config():
  if os.path.exists(CONFIG_PATH):
    return instance.export_dict()
  return {"current_db": None, "recent": None}


def set_current_db(path,backup=False):
    try:
      cur_history = instance.get('current_db')
    except Exception:
      cur_history = None
    finally:
      if cur_history != path:
        instance.update(('recent_db',cur_history))
      instance.update(('current_db',path))
      instance.update(('allow_backup',backup))
  
if __name__ == "__main__":
  pass
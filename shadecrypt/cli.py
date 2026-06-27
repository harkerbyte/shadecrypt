import sys,ast,socket,pickle
from shadeDB.core import shadeDB
from shadeDB.config import load_config,set_current_db
from shadeDB.service import is_true,server,red,blue,green,plain,yellow
red = '\x1b[1;31m'
green = '\x1b[1;32m'
plain = '\x1b[1;0m'
blue = '\x1b[1;34m'

def is_native(path):
  if path.endswith('.scdb'):
    return True
  return False

def handle_rq(token='',command='',key='',value='',admin_token='',multiple=False,port=8382):
  port = int(port)
  if is_true(token,load_config().get('token','null')):
    if command in ["get","id","pull"]:
      try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
          s.connect(('127.0.0.1',port))
          if command == "get":
            request = {"token":token,"command":command,"key":key,"multiple":multiple}
          elif command == "id":
            request = {"token":token,"command":command,"key":key}
          else:
            request = {"token":token,"command":command,"admin_token":admin_token,"key":key}
          request = pickle.dumps(request)
          s.sendall(request)
          receive = s.recv(5120)
          if receive:
            response = pickle.loads(receive)
            if response['status'] == "OK":
              print(response.get('data','null'))
            else:
              print(response.get('message','An error occured'))
      except ConnectionRefusedError:
        print(f"{red}O{plain}ops! connection was refused,are you sure the server is running?")
      finally:
        s.close()
        
    elif command in ["stop","clear","remove"]:
      try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
          s.connect(('127.0.0.1',port))
          if command == "stop":
              request = {"command":command,"token":token,"admin_token":admin_token}
              encode = pickle.dumps(request)
              s.sendall(encode)
              receive = s.recv(5120)
              if receive:
                response = pickle.loads(receive)
                if response['status'] == "OK":
                  print(f"{green}S{plain}uccessfully closed the server")
                else:
                  print(response.get('message','An error occured'))
          elif command in ["clear","remove"]:
            request = {"token":token,"admin_token":admin_token,"command":command,"key":key}

            request = pickle.dumps(request)
            s.sendall(request)
            receive = s.recv(5120)
            if receive:
              response = pickle.loads(receive)
              if response['status'] == "OK":
                print(response.get('message'))
              else:
                print(response.get('message'))
      except ConnectionRefusedError:
        print(f"{red}O{plain}ops! connection was refused,are you sure the server is running?")
      finally:
        s.close()
          
    elif command == "update":
      with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        try:
          s.connect(('127.0.0.1',port))
          request = {"token":token,"command":command,"admin_token":admin_token,"key":key,"value":value}
          request = pickle.dumps(request)
          s.sendall(request)
          receive = s.recv(5120)
          if receive:
            response = pickle.loads(receive)
            if response['status'] == "OK":
              print(response.get('message'))
            else:
              print(response.get('message'))
        except ConnectionRefusedError:
          print(f"{red}O{plain}ops! connection was refused,are you sure the server is running?")
        finally:
          s.close()
    elif command == "pull":
      with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        try:
          s.connect(('127.0.0.1',port))
          request = {"token":token,"command":command,"admin_token":admin_token,"key":key}
          request = pickle.dumps(request)
          s.sendall(request)
          receive = s.recv(5120)
          if receive:
            response = pickle.loads(receive)
            if response['status'] == "OK":
              print(response.get('message'))
            else:
              print(response.get('message'))
        except ConnectionRefusedError:
          print(f"{red}O{plain}ops! connection was refused,are you sure the server is running?")
        finally:
          s.close()
  else:
    pass
    
def correct(value):
  if value.upper() == "TRUE":
    return True
  elif value.upper() == "FALSE":
    return False
  else:
    try:
      return int(value)
    except ValueError:
      try:
        return float(value)
      except ValueError:
        try:
          return complex(value)
        except ValueError:
          return value

def main():
  loaded = load_config()
  if len(sys.argv) < 2:
    print('Usage: shadeDB [args...]')
    sys.exit(1)
  
  command = sys.argv[1]
  if command == "status":
    for key,val in loaded.items():
      print(f'{key} : {val}')
  
  args = sys.argv[2:]
  
  if command == "init":
    if not args:
      print(f'Usage: shadeDB init db_path/db_name.scdb  Enter : backup ; if you intend to allow backups otherwise leave empty \n\n{blue}E{plain}xample: shadeDB init mydb.scdb backup')
      sys.exit(1)
    db_path = args[0]
    bkup = True if len(args)>1 and args[1] == "backup" else False
    if is_native(db_path):
      shadedb = shadeDB(db_path,backup=bkup)
      set_current_db(db_path,backup=bkup)
      if shadedb.status() == "Active and running...":
        print(f'shadeDB : initialised {db_path} and already set as default database disk.')
      pass
    
    return
  
  if command == "use":
    if len(args) >= 1:
      db_path = args[0]
      bkup = True if len(args) > 1 and args[1] == "backup"  else False
      if is_native(db_path):
        set_current_db(db_path,backup=bkup)
        print(f'shadeDB: default db has been set to {green}{db_path}{plain}\nAllow backup : {bkup}')
    else:
      print(f'Usage: to change your current database disk\n{blue}E{plain}xample: shadeDB use newdb.scdb backup ')
    pass
  if command == "ls":
    print('Current db :%s'%load_config().get("current_db",None))
    
  if command == "start":
    port = args[0] if len(args) == 1 else 8382
    server(loaded.get('current_db'), backup = loaded.get('allow_backup',False),port = port)
    return
  
  if command in ["get","id"]:
    if len(args) >= 1:
      fetch = args[0]
      multiple = True if len(args) >= 2 and args[1] == "multiple" else False
      token = loaded.get('token')
      port = loaded.get('port',8382)
      handle_rq(token=token,command=command,key=fetch,multiple=multiple,port=port)
    else:
      print(f"""
Usage: 
shadeDB get key multiple
shadeDB id key - to fetch the given key's id

{blue}E{plain}xample : shadeDB get shade multiple
{blue}E{plain}xample2 : shadeDB get shade.age 
      
{yellow}O{plain}nly provide shade.age fetch the specified data from the key row - shade
      """)
  if command in ["stop","remove","clear"]:
    if len(args) >= 1:
      if command == "remove":
        target = args[0]
        handle_rq(token = loaded.get('token','null'),command = command,key = target,admin_token=loaded.get('admin_token','null'),port=loaded.get('port',8382))
    elif command in ["stop","clear"]:
      handle_rq(token = loaded.get('token','null'),command = command, admin_token = loaded.get('admin_token','null'),port=loaded.get('port',8382))
    else:
      print(f"""
Usage: 

{red}s{plain}hadecrypt remove key
{red}s{plain}hadecrypt stop - to close server remotely
{red}s{plain}hadecrypt clear - to clear the database record

{blue}E{plain}xample : shadeDB remove shade or shadeDB remove shade.age - remove the specified row data

{red}E{plain}xample2 : shadeDB stop - remotely close the database
{red}E{plain}xample3 : shadeDB clear - clear database

{yellow}R{plain}ead the full documentation at \'shadeDB pypi\' for a better understanding
      """)
  
  if command == "update":
    if len(args) > 1:
      key = args[0]
      value = args[1]
      if "." in key:
        construct = dict()
        key, pkey = key.split('.',1)
        construct[pkey] = correct(value)
        handle_rq(token=loaded.get('token','null'),admin_token=loaded.get('admin_token'),command=command,key=key,value=construct,port=loaded.get('port',8382))
      else:
        handle_rq(token=loaded.get('token','null'),admin_token=loaded.get('admin_token'),command=command,key=key,value=value,port=loaded.get('port',8382))
      
        
    else:
      print(f"""
Usage:

{red}s{plain}hadecrypt update key value

{blue}E{plain}xample : shadeDB update shade ola - single string
{blue}E{plain}xample2 : shadeDB update shade ['software engineer','shell','pentester','inventor'] - multiple values
{blue}E{plain}xample3 : shadeDB update shade {{"age":15,"status":"active","passion":"solving problems","skills":["python","js","engineering"]}} - mutiple key, value to populate the key row

{yellow}R{plain}ead the full documentation at \'shadeDB pypi\' for a better understanding
      """)
  
  if command == "pull":
    if len(args) == 1:
      key = args[0]
      if "." in key:
        handle_rq(token=loaded.get('token','null'),admin_token=loaded.get('admin_token'),command=command,key=key,port=loaded.get('port',8382))
      else:
        print(f"Do you mean to provide {red}{key}.data{plain}")
    else:
      print(f"""
Usage: 
        
{blue}s{plain}hadecrypt pull shade.age 
This should fetch the specified data from the provided row.
      """)
    
if __name__ == "__main__":
  pass
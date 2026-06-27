import socket,pickle,threading,random,string,datetime
from shadeDB.core import shadeDB
from shadeDB.__init__ import instance
red = '\x1b[1;31m'
green = '\x1b[1;32m'
plain = '\x1b[1;0m'
blue = '\x1b[1;34m'
yellow = '\x1b[1;33m'
def asc(port):
  asciii = f"""
███████╗   ██████╗  ██████╗    ██╗
██╔════╝  ██╔════╝  ██╔═══██╗  ██║
███████╗  ██║       ██║   ██║  ██████╗
╚════██║  ██║       ██║   ██║  ██╔══██╗
███████║  ██╚════╝  ╚██████╔╝  ██████╔╝
╚══════╝   ██████╝  ╚═════╝   ╚═════╝

Want some more? google search for 'harkerbyte'

{blue}S{plain}hadecrypt  server is up and running 
{blue}L{plain}istening on 127.0.0.1:{port}
{green}R{plain}eady for connections 
{yellow}D{plain}o not forget this is a beta version

{red}C{plain}trl-C to exit at will.
  """
  return asciii
def logger(address,status,command='get',queried='null',message='null'):
  if status == "OK":
    
    print(f'''
{datetime.datetime.now().strftime("%Y-%M-%d %H:%m")} {blue}{status}{plain} {command.upper()} - {queried if queried != 'null' else ''} {message if message != 'null' else ''}''')
  else:
        print(f'''
{datetime.datetime.now().strftime("%Y-%M-%d %H:%m")} {red}{status}{plain} {command.upper()} - {queried if queried != 'null' else ''} {message}''')

def is_true(new,comp):
  if new == comp:
    return True
  return False
  
def server(db_path,backup,port=8382):
    shutdown = False
    db = shadeDB(db_path, backup=backup,silent=True)
    dead_key = "".join(random.choice(string.ascii_letters+string.digits) for _ in range(8))
    admin_key = "".join(random.choice(string.ascii_letters+string.digits) for _ in range(24))
    instance.update(('token',dead_key))
    instance.update(('admin_token',admin_key))
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
      s.bind(('127.0.0.1',int(port)))
      s.listen(2)
      print(asc(port))
      instance.update(('port',port))
      try:
        while True:
          conn,addr = s.accept()
          with conn:
            re = conn.recv(5120)
            if not re:
              continue
            try:
              request = pickle.loads(re)
              auth_key = request.get('token',None)
              stored_key = instance.get('token')
              cmd = request.get("command")
              if is_true(auth_key,stored_key):
                if cmd in ["get","id","pull"]:
                  if cmd == "get":
                    if request.get("multiple",False):
                      data = db.get(request["key"],multiple=True)
                    else:
                      data = db.get_context(request.get("key")) or db.get(request.get("key"))
                    response = {"status":'OK',"data":data}
                  elif cmd == "id":
                    data = db.get_id(request.get('key'),multiple=True)
                    response = {"status":"OK","data":data}
                  else:
                    if is_true(request.get("admin_token"),admin_key):
                      data = db.get(request.get("key"))
                      response = {"status":"OK","data":data}
                    else:
                      response = {"status":"REQUEST DECLINED","message":"admin Authentication error"}
                elif cmd == "stop":
                  if is_true(request.get("admin_token",None),admin_key):
                    response = {"status":"OK","message":"Request to close the server, was granted"}
                    shutdown = True if cmd == "stop" else False
                  else:
                    response = {"status":"REQUEST DECLINED","message":"admin Authentication error"}
                elif cmd == "update":
                  if is_true(request.get('admin_token','null'),admin_key):
                    key = request.get('key')
                    value = request.get('value')
                    db.update((key,value))
                    response = {"status":"OK","message":f"Updated {key}"}
                  else:
                    response = {"status":"DECLINED","message":"admin Authentication error"} 
                elif cmd in ["clear","remove"]:
                  if is_true(request.get('admin_token'),admin_key):
                    if cmd == "remove":
                      db.remove(request.get('key'))
                      response = {"status":"OK","key":request.get('key','null'),"message":"Done"}
                    elif cmd == "clear":
                      db.clear()
                      response = {"status":"OK","key":request.get('key','null'),"message":"Cleared database"}
                  else:
                    response = {"status":"NOT ALLOWED","message":"Authentication error"}
                else:
                  response = {"status":'Not allowed',"message":'unknown command'}
              else:
                response = {"status":'Declined',"message":'Authentication error'}
            except Exception as error:
              response = {"status":'Error',"message":f'{error}'}
            except KeyboardInterrupt:
              s.close()
            logger(address=addr,status=response['status'],command=cmd,queried=request.get('key','null'),message=response.get('message','null'))
            encoded = pickle.dumps(response)
            conn.sendall(encoded)
            if cmd == "stop" and shutdown:
              s.close()
              break
      except Exception as error:
        response = {"status":'Error',"message":f'{error}'}
        encode = pickle.dumps(response)
        s.sendall(encode)
        logger(address=addr,status=response['status'],command=cmd,queried=request.get('key','null'),message=response.get('message','null'))
      except KeyboardInterrupt:
        s.close()
    
if __name__ == "__main__":
  pass
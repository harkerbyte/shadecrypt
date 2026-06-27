import os,re,threading,time,random,string
from shadeDB.schedule import Work
from shadeDB.exceptions import *

hologram = """\x1b[1;34m
Dev : shade\n
Brand : Harkerbyte\n
Github : https://github.com/harkerbyte\n
Support : https://harkerbyte.github.io/portfolio

Estimated compile durations :
10,000 columns,  < 50thousand chars ~ under 1sec
100,000 columns, > 3.6 million chars ~ under 4secs
1,000,000 columns, > 38 million chars ~ under 50 seconds
 

Guaranteed 96.1% uptime,while query returns in milliseconds.

Keep instance alive to avoid compile time delays except in case of importing an already existing DB instance.

Documentation : https://github.com/harkerbyte/shadeDB\x1b[1;0m
"""
class shadeDB:
  def __init__(self,file:str,write:bool=True,id:bool=True,backup:bool=False,silent:bool=False):
    self.file = file
    self.write = write
    self.backup = backup
    self.silent = silent
    self.id = id
    self.action = None
    self.checked = 0
    self.segments = None
    self.staged = None
    self.nesting = []
    self.acquiring = []
    self.state = "idle"
    self.buffer = ''
    self.ids = []
    self.keys = []
    self.values = []
    self.all = []
    self.preloaded = []
    self.backup = []
    self.valuation = False
    self.universal_dict = dict()
    self.compiled = False
    self.time_taken = None
    self.worker = Work()
    self.lock = threading.Lock()
    self.event = threading.Event()
    if self.file:
      self.monitor = threading.Thread(target=self.itPending, daemon=True)
      self.monitor.start()
    
  def crash(self,message):
    if message:
      print(message)
    self.run=False
    self.event.set()

  def itPending(self):
    if not self.compiled:
      self.compile()
  
  def __create__db__instance(self):
    kr = open(self.file, "w")
    kr.close()
    if not self.silent:
      print(f'{hologram}{self.file} \x1b[1;32mDB instance created, you can safely begin making changes now\x1b[1;0m 🙂')
  def get_content(self):
    if os.path.exists(self.file):
      with open(self.file, 'r') as content:
        return content.read()
    else:
      self.__create__db__instance()
      return self.get_content()
  
  def compile(self):
    with self.lock:
      self.compiled = False
      if isinstance(self.file, str):
        if self.file.endswith('.scdb'):
          self.segments = str(self.get_content())
          try:
            self.mapOut()
          except Exception as error:
            self.crash(error)
        else:
          self.crash(f'{self.file} doesn\'t appear to be a native : .scdb')
      elif isinstance(self.file, dict):
        self.segments = self.file
        try:
          self.import_dict(self.segments)
        except Exception as error:
          self.crash(error)
   
  def __backup__data__(self):
    self.backup = self.preloaded.copy()
    if self.backup and isinstance(self.file, str):
      if '/' in str(self.file):
        save = '/'.join(each for each in self.file.split('/')[0:-1] if each.strip())
        try:
          self.worker.add_task(self.__write__out__(to=f'/{save}/backup.scdb'))
        except FileNotFoundError:
          self.worker.add_task(self.__write__out__(to=f'{save}/backup.scdb'))
        return True
      else:
        self.worker.add_task(self.__write__out__(to='backup.scdb'))
        return True
    return True
  
  def conc_nest(self):
    self.staged, self.nest = None , False
    self.conclude = False
    self.nesting.clear()
    
  def run_nests(self):
    use = []
    if self.staged != None:
      if len(self.nesting) % 2 == 0 and len(self.nesting) > 1:
        for i in range(0, len(self.nesting), 2):
          if i + 1 <= len(self.nesting):
            use.append((self.nesting[i],self.nesting[i+1]))
            
          else:
            raise CompileError(f"-> {self.nesting[:]} <- Error")
        self.values.append(use)
        self.conc_nest()
      else:
        raise CompileError(f"->\x1b[1;41m{self.staged} : nesting error {self.nesting[:]}\x1b[1;0m <- key ~ val Error")
          
            
  def reset_buffer(self):
        self.buffer = ''
  #For later
  def deflate(self,container):
    result = []
    if isinstance(container,tuple):
      for each in container:
        if each.strip():
          result.append(each)
      return tuple(result)
    elif isinstance(container, list):
      for key,val in container:
        if key.strip() and val.strip():
          result.append((key,val))
      return result
    else:
      if isinstance(container,str):
        return ''.join(e.strip() for e in container)
        
  def mapOut(self):
        started = time.perf_counter()
        
        for i, ch in enumerate(self.segments):
          if self.state == "idle":
            if ch.isspace():
              continue
            elif ch == '"':
              self.state = "key"
              self.buffer+= ch
            elif ch.strip():
              pass
            else:
              raise NoKeyError(f'Missing key: after \x1b[1;41m {self.keys[-1:][0] if self.keys else 'first column'} \x1b[1;0m')
          elif self.state == "key":
            self.buffer += ch
            if ch == '"' and not self.is_escaped():
              self.keys.append(self.buffer[1:-1])
              self.reset_buffer()
              self.state = "colon"
              
          elif self.state == "colon":
            if ch.isspace():
              continue
            elif ch ==  ":":
              self.state = "value"
            else:
              raise AssignError(f'Missing colon ":", after \x1b[1;41m{self.keys[-1:][0] if self.keys else 'first column'} \x1b[1;0m')
              
          elif self.state == "value":
            if ch.isspace():
              continue
            elif ch == "`":
              self.state = "flat_value"
              self.buffer += ch
            elif ch == "[":
              self.state = "flat_array"
            elif ch == "{":
              self.state = "nest_key"
              self.staged = self.keys[-1:][0] if self.keys else None
          
          elif self.state == "flat_value":
            self.buffer += ch
            if ch == "`" and not self.is_escaped():
              self.values.append(self.escape_inputs(self.buffer[1:-1]))
              self.reset_buffer()
              self.state = "idle"
          
          elif self.state == "flat_array":
            if ch.isspace():
              continue
            elif ch == "`":
              self.buffer += ch
              self.state = "flat_array_value_assign"
            elif ch == "]":
              self.values.append(tuple(self.acquiring))
              self.acquiring.clear()
              self.state = "idle"
          
          elif self.state == "flat_array_value_assign":
            self.buffer += ch
            if ch == "`" and not self.is_escaped():
              self.acquiring.append(self.escape_inputs(self.buffer[1:-1]))
              self.reset_buffer()
              self.state = "flat_array"
              
          elif self.state == "nest_key":
            if ch.isspace():
              continue
            elif ch == '"':
              self.buffer += ch
              self.state = "nest_key_assign"
            elif ch == "}":
              self.run_nests()
              self.state = "idle"
            elif ch.strip():
              pass
            else:
              raise NoKeyError(f'Missing nested key: check row ->  \x1b[1;41m{self.keys[-1:][0] if self.keys else 'first row'}\x1b[1;0m')
              
          elif self.state == "nest_key_assign":
            self.buffer += ch
            if ch == '"' and not self.is_escaped():
              self.nesting.append(self.escape_inputs(self.buffer[1:-1]))
              self.reset_buffer()
              self.state = "nest_colon"
          
          elif self.state == "nest_colon":
            if ch.isspace():
              continue
            elif ch == ":":
              self.state = "nest_value"
            else:
              raise AssignError(f'Missing colon ":", after \x1b[1;41m{self.keys[-1:][0] if self.keys else 'first column'} \x1b[1;0m')
          
          elif self.state == "nest_value":
            if ch.isspace():
              continue
            elif ch == "`":
              self.buffer += ch
              self.state = "nest_flat_value"
            elif ch == "[":
              self.state = "nest_array_value"
          
          elif self.state == "nest_flat_value":
            self.buffer += ch
            if ch == '`' and not self.is_escaped():
              self.nesting.append(self.escape_inputs(self.buffer[1:-1]))
              self.reset_buffer()
              self.state = "nest_key"
          
          elif self.state == "nest_array_value":
            if ch.isspace():
              continue
            elif ch == "`":
              self.state = "nest_array_value_assign"
              self.buffer += ch
            elif ch == "]":
              self.state = "nest_key"
              self.nesting.append(tuple(self.acquiring))
              self.acquiring.clear()
        
          elif self.state == "nest_array_value_assign":
            self.buffer += ch
            if ch == "`" and not self.is_escaped():
              self.acquiring.append(self.escape_inputs(self.buffer[1:-1]))
              self.reset_buffer()
              self.state = "nest_array_value"
        
        self.time_taken = time.perf_counter() - started
        self.compiled = True
        self.id_each()

  #Helper to check if last char is escaped
  def is_escaped(self):
        backslashes = 0
        for c in self.buffer[-2:]:
            if c == "\\":
                backslashes += 1
            else:
                break
        return backslashes % 2 == 1
        
  def id_each(self):
    self.all.clear()
    if self.compiled:
      if self.keys:
        for i in range(len(self.keys)):
          the_key = self.keys[i]
          the_value = self.values[i]
        
          self.ids.append(int(i+1))
          self.all.append((int(i+1),the_key,the_value))
          self.universe_it(the_key, the_value)
          self.preloaded.append((the_key,the_value))
        
        return self.preload()
    
  def get_id(self,key:str = None,multiple=False):
    with self.lock:
      if self.compiled:
        if key in self.keys:
          if self.id:
            results = []
            for i in range(len(self.all)):
              id,keys,values = self.all[i]
              if key.strip() == keys:
                results.append(int(id))
                if not multiple:
                  break
            return results if results else None
          else:
            for i,k,v in self.all:
              if key == k:
                return int(i)
        else:
          raise NoKeyError(f'Key : {key} -> does not exist')
  
  def preload(self):
    if self.compiled and self.preloaded:
      return True
    return self.status()
    
  def items(self):
    with self.lock:
      if self.id:
        return self.all
      else:
        if self.preloaded:
          return self.preloaded
      
  
  def universe_it(self, key, value):
    if key not in self.universal_dict:
      self.universal_dict[key] = value
    else:
      i = 0
      while i >= 0:
        new = key + str(i)
        if new not in self.universal_dict:
          self.universal_dict[new] = value
          break
        i += 1
      
  
  #Update/Modify received datas
  def filter(self,value,init=None):
    final = []
    if isinstance(value, dict):
      #Has an existing nested dictionary
      if isinstance(init, list):
        merged = dict(init)
        merged.update(value)
        for key, val in merged.items():
          if isinstance(val,str) or isinstance(val,int) or isinstance(val,bool):
            final.append((key,val))
          elif isinstance(val,list) or isinstance(val,tuple) or isinstance(val,set):
            ap = []
            for e in val:
              ap.append(e)
          
            final.append((key,tuple(ap)))
        return final
      #Has no existing nested dictionary/new data not unique
      else:
        for key,val in value.items():
          if isinstance(val,str) or isinstance(val,int) or isinstance(val,bool):
            final.append((key,val))
          elif isinstance(val,list) or isinstance(val,tuple) or isinstance(val,set):
            ap = []
            for e in val:
              ap.append(e)
            final.append((key,tuple(ap)))
        return final
    #Has an array of data [shadecrypt term] stored as tuples/set/list
    elif isinstance(value,tuple) or isinstance(value,set) or isinstance(value,list):
      for e in value:
        final.append(e)
      return tuple(final)
    #Single data
    else:
      return value
  
  def escape_inputs(self, Uinput):
    if isinstance(Uinput, str):
        assemble = ''
        if Uinput:
            for i in range(len(Uinput)):
                if Uinput[i] != '`':
                    assemble += Uinput[i]
                else:
                    # backtick found
                    if i > 0 and Uinput[i-1] == '\\':
                        # remove the last char (the backslash)
                        assemble = assemble[:-1]
                        # add literal backtick
                        assemble += '`'
                    else:
                        # keep the backtick normally
                        assemble += '`'
        return assemble
    return Uinput
  
  def escape_outputs(self,Output):
    if isinstance(Output,str):
      assemble = ''
      if Output:
        for e in range(len(Output)):
          if Output[e] == '`' and Output[e-1] != '\\':
            assemble += '\\'
          assemble += Output[e]
        return assemble
    else:
      return Output
  
  def get_context(self,key:str or int = None, multiple:bool = True):
    with self.lock:
      final = dict()
      if isinstance(key,str):
        for keys,values in self.preloaded:
          if key == keys:
            if isinstance(values,list):
              for k,v in values:
                  final.update({k:v})
            else:
              return values
          pass
        return final
      
      elif isinstance(key,int):
        for ids,keys,values in self.all:
          if key == ids:
            if isinstance(values,list):
              for k,v in values:
                final.update({k:v})
              return final
            else:
              return values
          pass
        
  #Make changes
  def update(self,item,unique:bool = True):
    start = time.perf_counter()
    with self.lock:
      if self.__backup__data__():
        copied = self.all.copy()
        if unique:
          key,value = item
          if key in self.keys or key in self.ids:
            self.all.clear()
            self.temp_clear()
            for id, keys, values in copied:
              if isinstance(key, str):
                if key == keys:
                  vresult = self.filter(value,values)
                  self.all.append((id,keys,vresult))
                  self.universe_it(keys,vresult)
                  self.preloaded.append((keys,vresult))
                  self.values.append(vresult)
                  self.keys.append(key)
                  self.ids.append(id)
                else:
                  vvresult = self.filter(values)
                  self.all.append((id,keys,vvresult))
                  self.preloaded.append((keys,vvresult))
                  self.values.append(vvresult)
                  self.keys.append(keys)
                  self.ids.append(id)
              else:
                if int(key) == id:
                  ivresult = self.filter(value,values)
                  self.all.append((id,keys,ivresult))
                  self.universe_it(keys,ivresult)
                  self.preloaded.append((keys,ivresult))
                  self.values.append(ivresult)
                  self.keys.append(keys)
                  self.ids.append(id)
                else:
                  ivvresult = self.filter(values)
                  self.all.append((id,keys,ivvresult))
                  self.preloaded.append((keys,ivvresult))
                  self.values.append(ivvresult)
                  self.keys.append(keys)
                  self.ids.append(id) 
            end = time.perf_counter() - start
          else:
            innresult = self.filter(value)
            if isinstance(key, str):
              self.keys.append(key)
              self.values.append(innresult)
              self.all.append((len(copied) + 1, key, innresult))
              self.universe_it(key,innresult)
              self.preloaded.append((key,innresult))
          self.worker.add_task(self.__write__out__())
        else:
          key,value = item
          inresult = self.filter(value)
          self.ids.append(len(copied)+1)
          self.keys.append(key)
          self.values.append(inresult)
          self.all.append((len(copied)+1, key,inresult))
          self.universe_it(key, inresult)
          self.preloaded.append((key.strip(), inresult))
        self.worker.add_task(self.__write__out__())
      self.worker.add_task(self.__write__out__())
          
  def get(self, key:str | int = None , multiple:bool = False):
    with self.lock:
        if not key:
            return None
        # Handle nested keys (parent.child)
        if '.' in key:
          parent, child = key.split('.', 1)
          if parent not in self.keys:
            raise NoKeyError(f'Key : {parent} -> does not exist')
          results = [
            self.escape_outputs(cvalue) for pkey, pvalue in self.preloaded if pkey == parent
            for ckey, cvalue in pvalue if ckey == child
          ]
          if not results:
            raise NoValueError(f'Sub.key "{child}" does not exist')
          return results if multiple else results[0] if results else None
        # Handle flat keys
        if key not in self.keys:
          raise NoKeyError(f'Key : {key} -> does not exist')
        results = []
        if self.id:
          for _, k, v in self.all:
            if k == key:
              results.append(self.escape_outputs(v))
        else:
          for k, v in self.preloaded:
            if k == key:
              if isinstance(v, list) and len(v) == 1:
                results.append(self.escape_outputs(v[0]))
              else:
                results.append(v)
        if not results:
          return None
        return results if multiple else results[0]
        
  def get_by_id(self,id:int = None):
    with self.lock:
      if isinstance(id, int):
        if id in self.ids:
          for ids, keys, values in self.all:
            if ids == int(id):
              return values
        else:
          self.crash('ID : %i does not exist'%id)
      else:
        self.crash('ID : must be of integer type') 
    
  #Import python dictionary object
  def import_dict(self,dict_data:dict=None,overwrite:bool=False):
    if isinstance(dict_data, dict):
      if self.__backup__data__():
        self.temp_clear()
        for key, value in dict_data.items():
          self.keys.append(key)
          self.values.append(value)
        if overwrite:
          self.universal_dict.clear()
        self.id_each()
        self.action = self.__write__out__()
          
      else:
        raise DataTypeError(f'Data: must be dict tyoe not {type(dict_data)}')
  
  #Export datas as dictionary object      
  def export_dict(self):
    with self.lock:
      return self.universal_dict
  
  #Delete existing record   
  def remove(self,item:str | int = None):
    with self.lock:
      if self.__backup__data__():
        if isinstance(item, str):
          if '.' not in item:
            self.temp_clear()
            key = item
            for id,keys,value in self.all:
              if key == keys:
                self.all.remove((id,keys,value))
                break
            self.action = self.__write__out__()
          else:
            key,value = item.split('.')
            copied = self.all.copy()
            self.all.clear()
            self.preloaded.clear()
            for i in range(len(copied)):
              id,keys,values = copied[i]
              if key == keys:
                for keyin,valuein in values:
                  if value == keyin:
                    values.remove((keyin,valuein))
                    self.all.append((id,keys,values))
              else:
                self.all.append((id,keys,values))
        else:
          for ids,keys,values in self.all:
            id = item
            if id == ids:
              self.all.remove((ids,keys,values))
              break
          self.worker.add_task(self.__write__out__())
        self.worker.add_task(self.__write__out__())
    
        
  def temp_clear(self):
    self.ids.clear()
    self.keys.clear()
    self.values.clear()
    self.preloaded.clear()
    self.universal_dict.clear()
    
  def saturate(self):
    self.temp_clear()
    copied = self.all.copy()
    self.all.clear()
    for i in range(len(copied)):
      id,key,value = copied[i]
      self.ids.append(int(i+1))
      self.keys.append(key)
      self.values.append(value)
      self.all.append((int(i+1),key,value))
      self.preloaded.append((key,value))
      self.universe_it(key,value)
      
    return True
  
  def _format_values_(self,value):
    if isinstance(value, tuple):
      return "[" + " ,".join(f'`{self.escape_outputs(v)}`' for v in value) + "]"
    elif isinstance(value,list):
      return "{" + " ,".join(f'"{k}" : {'`%s`'%self.escape_outputs(str(v)) if not isinstance(v,tuple) else '[' + ' ,'.join('`%s`'%self.escape_outputs(str(val)) for val in v) + ']'}' for k,v in value) + "}"
    else:
      return f'`{self.escape_outputs(value)}`'
      
  def __write__out__(self,to=None):
    self.saturate()
    if self.write and isinstance(self.file,str) and to == None:
      if self.file.endswith('.scdb'):
        with open(self.file, 'w') as dload:
          for key, value in self.preloaded:
            dload.write(f'"{key}" : {self._format_values_(value)}\n')
        #print('done writing')
        return True
    elif self.write and to != None:
      with open(to, 'w') as filee:
        for key, value in self.backup:
          filee.write(f'"{key}" : {self._format_values_(value)}\n')
        self.backup.clear()
        #print('backup done')
      return True
    return True

  #Clear entire database
  def clear(self):
    with self.lock:
      if self.__backup__data__():
        self.temp_clear()
        self.all.clear()

        self.worker.add_task(self.__write__out__())
  
  #Storage engine status   
  def status(self):
    with self.lock:
      if self.compiled:
        return 'Active and running...'
      return 'Disabled'
  
  def __performance__(self):
    with self.lock:
      if self.compiled:
        return f'Compiled within : {self.time_taken}secs, number of columns : {len(self.preloaded)}'
      return None
  
if __name__ == "__main__":
  pass
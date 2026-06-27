import sys,time,threading
class Work:
  def __init__(self):
    self.pending = []
    self.timer = 0
  
  def add_task(self,func,*args,**kwargs):
    def runner():
      if self.pending:
        older = self.pending[:0]
        if older:
          self.pending.remove(older)
      
          funct,args,kwargs = older
          try:
            if self.timer == 0:
              funct(args,kwargs)
            else:
              time.sleep(self.timer)
              funct(args,kwargs)
          except Exception as error:
            sys.stdout.write(f'Error encounter : {error}, Running {funct.__name__}')
          finally:
            self.timer = 0
    
    if callable(func):
      if (func,args,kwargs) not in self.pending:
        self.pending.append((func,args,kwargs))
      else:
        self.timer += 5
    task = threading.Thread(target=runner,daemon=True)
    task.start()

      
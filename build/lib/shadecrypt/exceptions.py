class UnclosedError(Exception):
  def __init__(self,message):
    self.message = message
    super().__init__(f'You have an unclosed value `{message}`')
    """unclosed error message for sc.db"""
  
class CompileError(Exception):
  def __init__(self,at):
    self.at = at
    super().__init__(f'{self.at}')
    """compile error message for sc.db"""
 
class NoValueError(Exception):
  def __init__(self,message):
    self.message = message
    super().__init__(message)
    
  """ Value was not asssigned error"""
class NoKeyError(Exception):
  def __init__(self,message):
    self.message = message
    super().__init__(message)
  
  """Key does not exist error"""
class AssignError(Exception):
  def __init__(self,message):
    self.message = message
    super().__init__(message)
  """ Key to value was not assigned """
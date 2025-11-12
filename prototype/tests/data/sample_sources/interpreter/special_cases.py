
'''
ensure that YieldException is not generically handled in
eval loop, and also specifically in eval_Try
'''
from contextlib import contextmanager

def error_printer_context():
    try:
       yield 1
    except Exception as e:
       print(f"An error occurred: {e}")
a = list(error_printer_context())
print(a)



'''
ensure that the exception raise inside the 
while block is passed to the context manger 

see more comments on GeneratorState class
'''
@contextmanager
def error_printer_context():
    try:
       yield 1
    except Exception as e:
       print(f"An error occurred(contextlib): {e}")


class ErorrPrinter:
   def __enter__(self):
      return self 
   
   def __exit__(self, exc_type, exc_val, exc_tb):
      if exc_val:
         print(f"An error occurred: {exc_val}")
         return True # so the the exception is suppressed
   


test_value = 1
with ErorrPrinter():
   test_value = 1/0

with error_printer_context():
   1/0

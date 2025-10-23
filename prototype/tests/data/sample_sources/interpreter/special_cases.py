def error_printer_context():
    try:
       yield 1
    except Exception as e:
       print(f"An error occurred: {e}")
a = list(error_printer_context())
print(a)

